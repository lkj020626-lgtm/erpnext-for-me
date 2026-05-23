import frappe
from frappe import _


def validate_stock_entry(doc, method):
    """Validate Stock Entry for material issue / manufacture."""
    if doc.stock_entry_type in ("Material Issue", "Manufacture"):
        for item in doc.items:
            if item.s_warehouse:
                actual_qty = frappe.db.get_value(
                    "Bin",
                    {"item_code": item.item_code, "warehouse": item.s_warehouse},
                    "actual_qty",
                ) or 0
                if item.qty > actual_qty:
                    frappe.throw(
                        _("第 {0} 行：{1} 在 {2} 库存不足（当前 {3}，需要 {4}）").format(
                            item.idx, item.item_code, item.s_warehouse, actual_qty, item.qty
                        )
                    )


def on_submit_stock_entry(doc, method):
    """Log stock entry and check low stock warnings."""
    frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Stock Entry",
            "reference_name": doc.name,
            "content": _("{0} 由 {1} 于 {2} 提交").format(
                doc.stock_entry_type, frappe.session.user, frappe.utils.now()
            ),
        }
    ).insert(ignore_permissions=True)

    _check_low_stock_after_entry(doc)


def _check_low_stock_after_entry(doc):
    """After stock entry, check if any items fell below minimum stock."""
    for item in doc.items:
        warehouse = item.s_warehouse or item.t_warehouse
        if not warehouse:
            continue

        actual_qty = frappe.db.get_value(
            "Bin",
            {"item_code": item.item_code, "warehouse": warehouse},
            "actual_qty",
        ) or 0

        min_stock = frappe.db.get_value("Item", item.item_code, "custom_min_stock_qty") or 0
        safety_stock = frappe.db.get_value("Item", item.item_code, "safety_stock") or 0
        threshold = max(min_stock, safety_stock)

        if threshold > 0 and actual_qty <= threshold:
            frappe.publish_realtime(
                "msgprint",
                {
                    "message": _("库存预警：{0} 在 {1} 当前库存 {2}，低于最低库存 {3}").format(
                        item.item_code, warehouse, actual_qty, threshold
                    ),
                    "indicator": "orange",
                    "title": _("库存预警"),
                },
            )


@frappe.whitelist()
def get_low_stock_items(warehouse=None):
    """Get items below minimum stock level."""
    conditions = ""
    params = {}

    if warehouse:
        conditions = "AND b.warehouse = %(warehouse)s"
        params["warehouse"] = warehouse

    return frappe.db.sql(
        f"""
        SELECT
            b.item_code,
            i.item_name,
            i.custom_specification as specification,
            b.warehouse,
            b.actual_qty as current_qty,
            GREATEST(IFNULL(i.custom_min_stock_qty, 0), IFNULL(i.safety_stock, 0)) as min_qty,
            i.stock_uom
        FROM `tabBin` b
        JOIN `tabItem` i ON i.name = b.item_code
        WHERE i.disabled = 0
        AND GREATEST(IFNULL(i.custom_min_stock_qty, 0), IFNULL(i.safety_stock, 0)) > 0
        AND b.actual_qty <= GREATEST(IFNULL(i.custom_min_stock_qty, 0), IFNULL(i.safety_stock, 0))
        {conditions}
        ORDER BY (b.actual_qty - GREATEST(IFNULL(i.custom_min_stock_qty, 0), IFNULL(i.safety_stock, 0))) ASC
        """,
        params,
        as_dict=True,
    )


@frappe.whitelist()
def get_current_stock(item_code=None, warehouse=None, item_group=None):
    """Get current stock summary by item and warehouse."""
    conditions = []
    params = {}

    if item_code:
        conditions.append("b.item_code = %(item_code)s")
        params["item_code"] = item_code
    if warehouse:
        conditions.append("b.warehouse = %(warehouse)s")
        params["warehouse"] = warehouse
    if item_group:
        conditions.append("i.item_group = %(item_group)s")
        params["item_group"] = item_group

    where_clause = "WHERE i.disabled = 0 AND b.actual_qty != 0"
    if conditions:
        where_clause += " AND " + " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            b.item_code,
            i.item_name,
            i.custom_specification as specification,
            i.item_group,
            b.warehouse,
            b.actual_qty,
            b.reserved_qty,
            b.ordered_qty,
            b.projected_qty,
            i.stock_uom,
            GREATEST(IFNULL(i.custom_min_stock_qty, 0), IFNULL(i.safety_stock, 0)) as min_qty
        FROM `tabBin` b
        JOIN `tabItem` i ON i.name = b.item_code
        {where_clause}
        ORDER BY b.item_code, b.warehouse
        """,
        params,
        as_dict=True,
    )


@frappe.whitelist()
def get_stock_ledger(item_code=None, warehouse=None, from_date=None, to_date=None):
    """Get stock ledger entries for traceability."""
    conditions = []
    params = {}

    if item_code:
        conditions.append("sle.item_code = %(item_code)s")
        params["item_code"] = item_code
    if warehouse:
        conditions.append("sle.warehouse = %(warehouse)s")
        params["warehouse"] = warehouse
    if from_date:
        conditions.append("sle.posting_date >= %(from_date)s")
        params["from_date"] = from_date
    if to_date:
        conditions.append("sle.posting_date <= %(to_date)s")
        params["to_date"] = to_date

    where_clause = "WHERE 1=1"
    if conditions:
        where_clause += " AND " + " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            sle.posting_date,
            sle.posting_time,
            sle.item_code,
            i.item_name,
            sle.warehouse,
            sle.actual_qty as qty_change,
            sle.qty_after_transaction as balance_qty,
            sle.voucher_type,
            sle.voucher_no,
            sle.batch_no,
            sle.valuation_rate as unit_price
        FROM `tabStock Ledger Entry` sle
        JOIN `tabItem` i ON i.name = sle.item_code
        {where_clause}
        ORDER BY sle.posting_date DESC, sle.posting_time DESC
        LIMIT 500
        """,
        params,
        as_dict=True,
    )
