import frappe
from frappe import _


def validate_purchase_order(doc, method):
    """Validate Purchase Order before save."""
    for item in doc.items:
        if item.qty <= 0:
            frappe.throw(_("第 {0} 行：数量必须大于0").format(item.idx))
        if item.rate <= 0:
            frappe.throw(_("第 {0} 行：单价必须大于0").format(item.idx))


def on_submit_purchase_order(doc, method):
    """Log purchase order submission."""
    frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Purchase Order",
            "reference_name": doc.name,
            "content": _("采购订单由 {0} 提交").format(frappe.session.user),
        }
    ).insert(ignore_permissions=True)


def validate_purchase_receipt(doc, method):
    """Validate Purchase Receipt before save."""
    for item in doc.items:
        if item.qty <= 0:
            frappe.throw(_("第 {0} 行：入库数量必须大于0").format(item.idx))

        if item.purchase_order:
            po_item_qty = frappe.db.get_value(
                "Purchase Order Item",
                {"parent": item.purchase_order, "item_code": item.item_code},
                "qty",
            )
            if po_item_qty:
                already_received = frappe.db.sql(
                    """
                    SELECT IFNULL(SUM(pri.qty), 0)
                    FROM `tabPurchase Receipt Item` pri
                    JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
                    WHERE pri.purchase_order = %s
                    AND pri.item_code = %s
                    AND pr.docstatus = 1
                    AND pr.name != %s
                    """,
                    (item.purchase_order, item.item_code, doc.name),
                )[0][0]
                remaining = po_item_qty - already_received
                if item.qty > remaining:
                    frappe.msgprint(
                        _("第 {0} 行：入库数量 {1} 超过采购订单剩余数量 {2}，请确认是否为超收").format(
                            item.idx, item.qty, remaining
                        ),
                        alert=True,
                    )


def on_submit_purchase_receipt(doc, method):
    """Log purchase receipt submission with operator info."""
    frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Purchase Receipt",
            "reference_name": doc.name,
            "content": _("采购入库由 {0} 于 {1} 确认").format(
                frappe.session.user, frappe.utils.now()
            ),
        }
    ).insert(ignore_permissions=True)
