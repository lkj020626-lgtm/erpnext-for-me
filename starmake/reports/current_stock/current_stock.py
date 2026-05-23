import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "item_code", "label": _("商品编码"), "fieldtype": "Link", "options": "Item", "width": 120},
        {"fieldname": "item_name", "label": _("商品名称"), "fieldtype": "Data", "width": 150},
        {"fieldname": "specification", "label": _("规格型号"), "fieldtype": "Data", "width": 100},
        {"fieldname": "item_group", "label": _("分类"), "fieldtype": "Link", "options": "Item Group", "width": 100},
        {"fieldname": "warehouse", "label": _("仓库"), "fieldtype": "Link", "options": "Warehouse", "width": 120},
        {"fieldname": "actual_qty", "label": _("当前库存"), "fieldtype": "Float", "width": 90},
        {"fieldname": "reserved_qty", "label": _("已预留"), "fieldtype": "Float", "width": 80},
        {"fieldname": "ordered_qty", "label": _("已订购"), "fieldtype": "Float", "width": 80},
        {"fieldname": "projected_qty", "label": _("预计库存"), "fieldtype": "Float", "width": 90},
        {"fieldname": "stock_uom", "label": _("单位"), "fieldtype": "Data", "width": 60},
        {"fieldname": "min_qty", "label": _("最低库存"), "fieldtype": "Float", "width": 80},
    ]


def get_data(filters):
    conditions = []
    params = {}

    if filters and filters.get("item_code"):
        conditions.append("b.item_code = %(item_code)s")
        params["item_code"] = filters["item_code"]
    if filters and filters.get("warehouse"):
        conditions.append("b.warehouse = %(warehouse)s")
        params["warehouse"] = filters["warehouse"]
    if filters and filters.get("item_group"):
        conditions.append("i.item_group = %(item_group)s")
        params["item_group"] = filters["item_group"]

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
