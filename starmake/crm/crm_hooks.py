"""
StarMake CRM / After-sales Module
- Customer follow-up tracking
- Service tickets
- Warranty management
- On-site service records
- Customer satisfaction
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_customer_followup_list(sales_person=None, status=None):
    """Get customer follow-up tasks."""
    conditions = ["1=1"]
    params = {}

    if sales_person:
        conditions.append("t.allocated_to = %(sales_person)s")
        params["sales_person"] = sales_person
    if status:
        conditions.append("t.status = %(status)s")
        params["status"] = status
    else:
        conditions.append("t.status != 'Cancelled'")

    where_clause = " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            t.name, t.subject, t.status, t.priority,
            t.allocated_to, t.exp_end_date,
            t.reference_type, t.reference_name,
            c.customer_name
        FROM `tabToDo` t
        LEFT JOIN `tabCustomer` c ON c.name = t.reference_name AND t.reference_type = 'Customer'
        WHERE {where_clause}
        ORDER BY t.exp_end_date ASC
        LIMIT 100
        """,
        params,
        as_dict=True,
    )


@frappe.whitelist()
def create_followup_task(customer, subject, assigned_to, due_date, description=None):
    """Create a customer follow-up task."""
    todo = frappe.get_doc(
        {
            "doctype": "ToDo",
            "subject": subject,
            "description": description or "",
            "reference_type": "Customer",
            "reference_name": customer,
            "allocated_to": assigned_to,
            "exp_end_date": due_date,
            "priority": "Medium",
            "status": "Open",
        }
    )
    todo.insert(ignore_permissions=True)
    frappe.db.commit()
    return todo.name


def on_issue_update(doc, method):
    """Track issue resolution for after-sales."""
    if doc.status == "Closed" and doc.has_value_changed("status"):
        frappe.get_doc(
            {
                "doctype": "Comment",
                "comment_type": "Info",
                "reference_doctype": "Issue",
                "reference_name": doc.name,
                "content": _("售后工单由 {0} 于 {1} 关闭，解决方案：{2}").format(
                    frappe.session.user, frappe.utils.now(), doc.resolution_details or "无"
                ),
            }
        ).insert(ignore_permissions=True)


@frappe.whitelist()
def get_warranty_items(customer=None):
    """Get items under warranty for a customer."""
    conditions = ["dn.docstatus = 1"]
    params = {}

    if customer:
        conditions.append("dn.customer = %(customer)s")
        params["customer"] = customer

    where_clause = " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            dn.customer, dn.customer_name,
            dni.item_code, dni.item_name, dni.serial_no,
            dn.posting_date as delivery_date,
            i.warranty_period,
            DATE_ADD(dn.posting_date, INTERVAL IFNULL(i.warranty_period, 0) DAY) as warranty_end_date
        FROM `tabDelivery Note Item` dni
        JOIN `tabDelivery Note` dn ON dn.name = dni.parent
        JOIN `tabItem` i ON i.name = dni.item_code
        WHERE {where_clause}
        AND i.warranty_period > 0
        AND DATE_ADD(dn.posting_date, INTERVAL i.warranty_period DAY) >= CURDATE()
        ORDER BY warranty_end_date ASC
        """,
        params,
        as_dict=True,
    )


@frappe.whitelist()
def get_service_summary(from_date=None, to_date=None):
    """Get after-sales service summary."""
    conditions = ["1=1"]
    params = {}

    if from_date:
        conditions.append("creation >= %(from_date)s")
        params["from_date"] = from_date
    if to_date:
        conditions.append("creation <= %(to_date)s")
        params["to_date"] = to_date

    where_clause = " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            status,
            priority,
            COUNT(*) as count,
            AVG(TIMESTAMPDIFF(HOUR, creation, modified)) as avg_resolution_hours
        FROM `tabIssue`
        WHERE {where_clause}
        GROUP BY status, priority
        ORDER BY FIELD(status, 'Open', 'Replied', 'Resolved', 'Closed')
        """,
        params,
        as_dict=True,
    )
