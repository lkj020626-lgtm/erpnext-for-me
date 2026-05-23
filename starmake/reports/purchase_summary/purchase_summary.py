import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart


def get_columns():
    return [
        {"fieldname": "supplier", "label": _("供应商"), "fieldtype": "Link", "options": "Supplier", "width": 150},
        {"fieldname": "item_code", "label": _("商品编码"), "fieldtype": "Link", "options": "Item", "width": 120},
        {"fieldname": "item_name", "label": _("商品名称"), "fieldtype": "Data", "width": 150},
        {"fieldname": "total_qty", "label": _("总数量"), "fieldtype": "Float", "width": 90},
        {"fieldname": "total_amount", "label": _("总金额"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "order_count", "label": _("订单数"), "fieldtype": "Int", "width": 70},
        {"fieldname": "stock_uom", "label": _("单位"), "fieldtype": "Data", "width": 60},
    ]


def get_data(filters):
    conditions = []
    params = {}

    if filters and filters.get("from_date"):
        conditions.append("po.transaction_date >= %(from_date)s")
        params["from_date"] = filters["from_date"]
    if filters and filters.get("to_date"):
        conditions.append("po.transaction_date <= %(to_date)s")
        params["to_date"] = filters["to_date"]
    if filters and filters.get("supplier"):
        conditions.append("po.supplier = %(supplier)s")
        params["supplier"] = filters["supplier"]
    if filters and filters.get("item_code"):
        conditions.append("poi.item_code = %(item_code)s")
        params["item_code"] = filters["item_code"]

    where_clause = "WHERE po.docstatus = 1"
    if conditions:
        where_clause += " AND " + " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            po.supplier,
            poi.item_code,
            poi.item_name,
            SUM(poi.qty) as total_qty,
            SUM(poi.amount) as total_amount,
            COUNT(DISTINCT po.name) as order_count,
            poi.stock_uom
        FROM `tabPurchase Order Item` poi
        JOIN `tabPurchase Order` po ON po.name = poi.parent
        {where_clause}
        GROUP BY po.supplier, poi.item_code
        ORDER BY total_amount DESC
        """,
        params,
        as_dict=True,
    )


def get_chart(data):
    if not data:
        return None
    labels = [d.supplier for d in data[:10]]
    values = [d.total_amount for d in data[:10]]
    return {
        "data": {"labels": labels, "datasets": [{"name": _("采购金额"), "values": values}]},
        "type": "bar",
    }
