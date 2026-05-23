"""
StarMake Finance Module
- Chinese Chart of Accounts template
- AR/AP dashboard
- Customer/Supplier statement
- Simple gross profit
- Integration with buying/selling/stock
"""

import frappe
from frappe import _


def on_submit_sales_invoice(doc, method):
    """Log sales invoice and update customer balance."""
    frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Sales Invoice",
            "reference_name": doc.name,
            "content": _("销售发票由 {0} 于 {1} 提交，金额 {2}").format(
                frappe.session.user, frappe.utils.now(), doc.grand_total
            ),
        }
    ).insert(ignore_permissions=True)


def on_submit_purchase_invoice(doc, method):
    """Log purchase invoice."""
    frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Purchase Invoice",
            "reference_name": doc.name,
            "content": _("采购发票由 {0} 于 {1} 提交，金额 {2}").format(
                frappe.session.user, frappe.utils.now(), doc.grand_total
            ),
        }
    ).insert(ignore_permissions=True)


def on_submit_payment_entry(doc, method):
    """Log payment entry."""
    direction = "收款" if doc.payment_type == "Receive" else "付款"
    frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Payment Entry",
            "reference_name": doc.name,
            "content": _("{0}由 {1} 于 {2} 提交，金额 {3}").format(
                direction, frappe.session.user, frappe.utils.now(), doc.paid_amount
            ),
        }
    ).insert(ignore_permissions=True)


@frappe.whitelist()
def get_receivable_summary(customer=None, from_date=None, to_date=None):
    """Get accounts receivable summary."""
    conditions = ["si.docstatus = 1", "si.outstanding_amount > 0"]
    params = {}

    if customer:
        conditions.append("si.customer = %(customer)s")
        params["customer"] = customer
    if from_date:
        conditions.append("si.posting_date >= %(from_date)s")
        params["from_date"] = from_date
    if to_date:
        conditions.append("si.posting_date <= %(to_date)s")
        params["to_date"] = to_date

    where_clause = " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            si.customer,
            si.customer_name,
            COUNT(*) as invoice_count,
            SUM(si.grand_total) as total_amount,
            SUM(si.outstanding_amount) as outstanding_amount,
            MIN(si.posting_date) as oldest_invoice_date
        FROM `tabSales Invoice` si
        WHERE {where_clause}
        GROUP BY si.customer
        ORDER BY outstanding_amount DESC
        """,
        params,
        as_dict=True,
    )


@frappe.whitelist()
def get_payable_summary(supplier=None, from_date=None, to_date=None):
    """Get accounts payable summary."""
    conditions = ["pi.docstatus = 1", "pi.outstanding_amount > 0"]
    params = {}

    if supplier:
        conditions.append("pi.supplier = %(supplier)s")
        params["supplier"] = supplier
    if from_date:
        conditions.append("pi.posting_date >= %(from_date)s")
        params["from_date"] = from_date
    if to_date:
        conditions.append("pi.posting_date <= %(to_date)s")
        params["to_date"] = to_date

    where_clause = " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            pi.supplier,
            pi.supplier_name,
            COUNT(*) as invoice_count,
            SUM(pi.grand_total) as total_amount,
            SUM(pi.outstanding_amount) as outstanding_amount,
            MIN(pi.posting_date) as oldest_invoice_date
        FROM `tabPurchase Invoice` pi
        WHERE {where_clause}
        GROUP BY pi.supplier
        ORDER BY outstanding_amount DESC
        """,
        params,
        as_dict=True,
    )


@frappe.whitelist()
def get_customer_statement(customer, from_date=None, to_date=None):
    """Generate customer statement (对账单)."""
    params = {"customer": customer}
    date_filter = ""

    if from_date:
        date_filter += " AND posting_date >= %(from_date)s"
        params["from_date"] = from_date
    if to_date:
        date_filter += " AND posting_date <= %(to_date)s"
        params["to_date"] = to_date

    invoices = frappe.db.sql(
        f"""
        SELECT posting_date, name as voucher, 'Sales Invoice' as type,
               grand_total as debit, 0 as credit, outstanding_amount
        FROM `tabSales Invoice`
        WHERE customer = %(customer)s AND docstatus = 1 {date_filter}
        """,
        params,
        as_dict=True,
    )

    payments = frappe.db.sql(
        f"""
        SELECT posting_date, name as voucher, 'Payment Entry' as type,
               0 as debit, paid_amount as credit, 0 as outstanding_amount
        FROM `tabPayment Entry`
        WHERE party_type = 'Customer' AND party = %(customer)s
        AND docstatus = 1 AND payment_type = 'Receive' {date_filter}
        """,
        params,
        as_dict=True,
    )

    entries = sorted(invoices + payments, key=lambda x: x["posting_date"])
    balance = 0
    for entry in entries:
        balance += entry["debit"] - entry["credit"]
        entry["balance"] = balance

    return {"entries": entries, "closing_balance": balance}


@frappe.whitelist()
def get_supplier_statement(supplier, from_date=None, to_date=None):
    """Generate supplier statement (对账单)."""
    params = {"supplier": supplier}
    date_filter = ""

    if from_date:
        date_filter += " AND posting_date >= %(from_date)s"
        params["from_date"] = from_date
    if to_date:
        date_filter += " AND posting_date <= %(to_date)s"
        params["to_date"] = to_date

    invoices = frappe.db.sql(
        f"""
        SELECT posting_date, name as voucher, 'Purchase Invoice' as type,
               0 as debit, grand_total as credit, outstanding_amount
        FROM `tabPurchase Invoice`
        WHERE supplier = %(supplier)s AND docstatus = 1 {date_filter}
        """,
        params,
        as_dict=True,
    )

    payments = frappe.db.sql(
        f"""
        SELECT posting_date, name as voucher, 'Payment Entry' as type,
               paid_amount as debit, 0 as credit, 0 as outstanding_amount
        FROM `tabPayment Entry`
        WHERE party_type = 'Supplier' AND party = %(supplier)s
        AND docstatus = 1 AND payment_type = 'Pay' {date_filter}
        """,
        params,
        as_dict=True,
    )

    entries = sorted(invoices + payments, key=lambda x: x["posting_date"])
    balance = 0
    for entry in entries:
        balance += entry["credit"] - entry["debit"]
        entry["balance"] = balance

    return {"entries": entries, "closing_balance": balance}
