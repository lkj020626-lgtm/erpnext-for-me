import frappe
from frappe import _


def validate_work_order(doc, method):
    """Validate Work Order."""
    if doc.qty <= 0:
        frappe.throw(_("计划生产数量必须大于0"))

    if not doc.bom_no:
        frappe.throw(_("请选择 BOM（物料清单）"))

    bom_exists = frappe.db.exists("BOM", {"name": doc.bom_no, "is_active": 1})
    if not bom_exists:
        frappe.throw(_("BOM {0} 不存在或已停用").format(doc.bom_no))


def on_submit_work_order(doc, method):
    """Log work order submission."""
    frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Work Order",
            "reference_name": doc.name,
            "content": _("生产工单由 {0} 于 {1} 下达，计划生产 {2} {3}").format(
                frappe.session.user, frappe.utils.now(), doc.qty, doc.stock_uom
            ),
        }
    ).insert(ignore_permissions=True)


@frappe.whitelist()
def get_production_status_summary():
    """Get summary of work orders by status for dashboard."""
    return frappe.db.sql(
        """
        SELECT
            status,
            COUNT(*) as count,
            SUM(qty) as total_qty,
            SUM(produced_qty) as total_produced
        FROM `tabWork Order`
        WHERE docstatus = 1
        AND status IN ('Not Started', 'In Process', 'Completed', 'Stopped')
        GROUP BY status
        ORDER BY FIELD(status, 'In Process', 'Not Started', 'Completed', 'Stopped')
        """,
        as_dict=True,
    )


@frappe.whitelist()
def check_material_availability(work_order):
    """Check if raw materials are available for a work order."""
    wo = frappe.get_doc("Work Order", work_order)
    shortages = []

    for item in wo.required_items:
        actual_qty = frappe.db.get_value(
            "Bin",
            {"item_code": item.item_code, "warehouse": item.source_warehouse or wo.source_warehouse},
            "actual_qty",
        ) or 0

        required = item.required_qty - item.transferred_qty
        if required > actual_qty:
            shortages.append(
                {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "warehouse": item.source_warehouse or wo.source_warehouse,
                    "required_qty": required,
                    "available_qty": actual_qty,
                    "shortage": required - actual_qty,
                }
            )

    return {"has_shortage": len(shortages) > 0, "shortages": shortages}
