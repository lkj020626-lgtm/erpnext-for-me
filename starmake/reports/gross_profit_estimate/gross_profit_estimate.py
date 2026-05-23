import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    summary = get_summary(data)
    chart = get_chart(data)
    return columns, data, summary, chart


def get_columns():
    return [
        {"fieldname": "item_code", "label": _("商品编码"), "fieldtype": "Link", "options": "Item", "width": 120},
        {"fieldname": "item_name", "label": _("商品名称"), "fieldtype": "Data", "width": 150},
        {"fieldname": "total_sold_qty", "label": _("销售数量"), "fieldtype": "Float", "width": 90},
        {"fieldname": "selling_amount", "label": _("销售收入"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "avg_selling_rate", "label": _("平均售价"), "fieldtype": "Currency", "width": 100},
        {"fieldname": "avg_buying_rate", "label": _("平均成本"), "fieldtype": "Currency", "width": 100},
        {"fieldname": "gross_profit", "label": _("毛利"), "fieldtype": "Currency", "width": 100},
        {"fieldname": "gross_margin", "label": _("毛利率%"), "fieldtype": "Percent", "width": 80},
    ]


def get_data(filters):
    conditions = []
    params = {}

    if filters and filters.get("from_date"):
        conditions.append("dn.posting_date >= %(from_date)s")
        params["from_date"] = filters["from_date"]
    if filters and filters.get("to_date"):
        conditions.append("dn.posting_date <= %(to_date)s")
        params["to_date"] = filters["to_date"]
    if filters and filters.get("customer"):
        conditions.append("dn.customer = %(customer)s")
        params["customer"] = filters["customer"]
    if filters and filters.get("item_code"):
        conditions.append("dni.item_code = %(item_code)s")
        params["item_code"] = filters["item_code"]

    where_clause = "WHERE dn.docstatus = 1"
    if conditions:
        where_clause += " AND " + " AND ".join(conditions)

    data = frappe.db.sql(
        f"""
        SELECT
            dni.item_code,
            dni.item_name,
            SUM(dni.qty) as total_sold_qty,
            SUM(dni.amount) as selling_amount,
            ROUND(SUM(dni.amount) / SUM(dni.qty), 2) as avg_selling_rate
        FROM `tabDelivery Note Item` dni
        JOIN `tabDelivery Note` dn ON dn.name = dni.parent
        {where_clause}
        GROUP BY dni.item_code
        ORDER BY selling_amount DESC
        LIMIT 100
        """,
        params,
        as_dict=True,
    )

    for row in data:
        avg_buying = _get_avg_buying_rate(row.item_code)
        row["avg_buying_rate"] = avg_buying
        row["gross_profit"] = row["selling_amount"] - (avg_buying * row["total_sold_qty"])
        if row["selling_amount"]:
            row["gross_margin"] = round(row["gross_profit"] / row["selling_amount"] * 100, 1)
        else:
            row["gross_margin"] = 0

    return data


def _get_avg_buying_rate(item_code):
    """Get average buying rate from recent purchase receipts or valuation rate."""
    val_rate = frappe.db.get_value("Item", item_code, "valuation_rate")
    if val_rate:
        return val_rate

    custom_price = frappe.db.get_value("Item", item_code, "custom_purchase_price")
    if custom_price:
        return custom_price

    return 0


def get_summary(data):
    if not data:
        return []
    total_revenue = sum(d["selling_amount"] for d in data)
    total_profit = sum(d["gross_profit"] for d in data)
    avg_margin = round(total_profit / total_revenue * 100, 1) if total_revenue else 0

    return [
        {"label": _("总销售收入"), "value": total_revenue, "datatype": "Currency"},
        {"label": _("总毛利"), "value": total_profit, "datatype": "Currency"},
        {"label": _("综合毛利率"), "value": f"{avg_margin}%", "datatype": "Data"},
    ]


def get_chart(data):
    if not data:
        return None
    top_items = data[:10]
    labels = [d["item_name"] for d in top_items]
    profit_values = [d["gross_profit"] for d in top_items]
    return {
        "data": {"labels": labels, "datasets": [{"name": _("毛利"), "values": profit_values}]},
        "type": "bar",
        "colors": ["#28a745"],
    }
