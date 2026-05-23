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
        {"fieldname": "warehouse", "label": _("仓库"), "fieldtype": "Link", "options": "Warehouse", "width": 120},
        {"fieldname": "current_qty", "label": _("当前库存"), "fieldtype": "Float", "width": 90},
        {"fieldname": "min_qty", "label": _("最低库存"), "fieldtype": "Float", "width": 80},
        {"fieldname": "shortage", "label": _("缺口"), "fieldtype": "Float", "width": 80},
        {"fieldname": "stock_uom", "label": _("单位"), "fieldtype": "Data", "width": 60},
    ]


def get_data(filters):
    conditions = []
    params = {}

    if filters and filters.get("warehouse"):
        conditions.append("b.warehouse = %(warehouse)s")
        params["warehouse"] = filters["warehouse"]
    if filters and filters.get("item_group"):
        conditions.append("i.item_group = %(item_group)s")
        params["item_group"] = filters["item_group"]

    extra_where = ""
    if conditions:
        extra_where = " AND " + " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            b.item_code,
            i.item_name,
            i.custom_specification as specification,
            b.warehouse,
            b.actual_qty as current_qty,
            GREATEST(IFNULL(i.custom_min_stock_qty, 0), IFNULL(i.safety_stock, 0)) as min_qty,
            (GREATEST(IFNULL(i.custom_min_stock_qty, 0), IFNULL(i.safety_stock, 0)) - b.actual_qty) as shortage,
            i.stock_uom
        FROM `tabBin` b
        JOIN `tabItem` i ON i.name = b.item_code
        WHERE i.disabled = 0
        AND GREATEST(IFNULL(i.custom_min_stock_qty, 0), IFNULL(i.safety_stock, 0)) > 0
        AND b.actual_qty <= GREATEST(IFNULL(i.custom_min_stock_qty, 0), IFNULL(i.safety_stock, 0))
        {extra_where}
        ORDER BY shortage DESC
        """,
        params,
        as_dict=True,
    )
