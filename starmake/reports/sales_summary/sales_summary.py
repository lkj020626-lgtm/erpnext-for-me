import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart


def get_columns():
    return [
        {"fieldname": "customer", "label": _("客户"), "fieldtype": "Link", "options": "Customer", "width": 150},
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
        conditions.append("so.transaction_date >= %(from_date)s")
        params["from_date"] = filters["from_date"]
    if filters and filters.get("to_date"):
        conditions.append("so.transaction_date <= %(to_date)s")
        params["to_date"] = filters["to_date"]
    if filters and filters.get("customer"):
        conditions.append("so.customer = %(customer)s")
        params["customer"] = filters["customer"]
    if filters and filters.get("item_code"):
        conditions.append("soi.item_code = %(item_code)s")
        params["item_code"] = filters["item_code"]

    where_clause = "WHERE so.docstatus = 1"
    if conditions:
        where_clause += " AND " + " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            so.customer,
            soi.item_code,
            soi.item_name,
            SUM(soi.qty) as total_qty,
            SUM(soi.amount) as total_amount,
            COUNT(DISTINCT so.name) as order_count,
            soi.stock_uom
        FROM `tabSales Order Item` soi
        JOIN `tabSales Order` so ON so.name = soi.parent
        {where_clause}
        GROUP BY so.customer, soi.item_code
        ORDER BY total_amount DESC
        """,
        params,
        as_dict=True,
    )


def get_chart(data):
    if not data:
        return None
    labels = [d.item_name for d in data[:10]]
    values = [d.total_amount for d in data[:10]]
    return {
        "data": {"labels": labels, "datasets": [{"name": _("销售金额"), "values": values}]},
        "type": "bar",
    }
