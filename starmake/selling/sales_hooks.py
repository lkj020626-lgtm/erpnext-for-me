import frappe
from frappe import _


def validate_sales_order(doc, method):
    """Validate Sales Order before save."""
    for item in doc.items:
        if item.qty <= 0:
            frappe.throw(_("第 {0} 行：数量必须大于0").format(item.idx))
        if item.rate <= 0:
            frappe.throw(_("第 {0} 行：售价必须大于0").format(item.idx))


def on_submit_sales_order(doc, method):
    """Log sales order submission."""
    frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Sales Order",
            "reference_name": doc.name,
            "content": _("销售订单由 {0} 提交").format(frappe.session.user),
        }
    ).insert(ignore_permissions=True)


def validate_delivery_note(doc, method):
    """Validate Delivery Note - check stock sufficiency."""
    for item in doc.items:
        if item.qty <= 0:
            frappe.throw(_("第 {0} 行：出库数量必须大于0").format(item.idx))

        if item.against_sales_order:
            so_item_qty = frappe.db.get_value(
                "Sales Order Item",
                {"parent": item.against_sales_order, "item_code": item.item_code},
                "qty",
            )
            if so_item_qty:
                already_delivered = frappe.db.sql(
                    """
                    SELECT IFNULL(SUM(dni.qty), 0)
                    FROM `tabDelivery Note Item` dni
                    JOIN `tabDelivery Note` dn ON dn.name = dni.parent
                    WHERE dni.against_sales_order = %s
                    AND dni.item_code = %s
                    AND dn.docstatus = 1
                    AND dn.name != %s
                    """,
                    (item.against_sales_order, item.item_code, doc.name),
                )[0][0]
                remaining = so_item_qty - already_delivered
                if item.qty > remaining:
                    frappe.msgprint(
                        _("第 {0} 行：出库数量 {1} 超过销售订单剩余数量 {2}").format(
                            item.idx, item.qty, remaining
                        ),
                        alert=True,
                    )

        actual_qty = frappe.db.get_value(
            "Bin",
            {"item_code": item.item_code, "warehouse": item.warehouse},
            "actual_qty",
        ) or 0

        if item.qty > actual_qty:
            frappe.msgprint(
                _("第 {0} 行：{1} 在 {2} 的当前库存为 {3}，不足以出库 {4}").format(
                    item.idx, item.item_code, item.warehouse, actual_qty, item.qty
                ),
                indicator="orange",
                alert=True,
            )


def on_submit_delivery_note(doc, method):
    """Log delivery note submission with operator info."""
    frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Delivery Note",
            "reference_name": doc.name,
            "content": _("销售出库由 {0} 于 {1} 确认").format(
                frappe.session.user, frappe.utils.now()
            ),
        }
    ).insert(ignore_permissions=True)
