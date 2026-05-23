import frappe
from frappe import _


ITEM_IMPORT_COLUMNS = [
    {"fieldname": "item_code", "label": "商品编码", "required": True},
    {"fieldname": "item_name", "label": "商品名称", "required": True},
    {"fieldname": "custom_specification", "label": "规格型号", "required": False},
    {"fieldname": "item_group", "label": "商品分类", "required": True},
    {"fieldname": "stock_uom", "label": "单位", "required": True},
    {"fieldname": "standard_rate", "label": "销售单价", "required": False},
    {"fieldname": "custom_purchase_price", "label": "参考采购价", "required": False},
    {"fieldname": "custom_supplier_ref", "label": "默认供应商", "required": False},
    {"fieldname": "safety_stock", "label": "安全库存", "required": False},
    {"fieldname": "custom_min_stock_qty", "label": "最低库存", "required": False},
    {"fieldname": "description", "label": "描述", "required": False},
]

CUSTOMER_IMPORT_COLUMNS = [
    {"fieldname": "customer_name", "label": "客户名称", "required": True},
    {"fieldname": "customer_group", "label": "客户分组", "required": False},
    {"fieldname": "custom_contact_person", "label": "联系人", "required": False},
    {"fieldname": "custom_phone", "label": "联系电话", "required": False},
    {"fieldname": "custom_address_text", "label": "收货地址", "required": False},
    {"fieldname": "custom_remark", "label": "备注", "required": False},
]

SUPPLIER_IMPORT_COLUMNS = [
    {"fieldname": "supplier_name", "label": "供应商名称", "required": True},
    {"fieldname": "supplier_group", "label": "供应商分组", "required": False},
    {"fieldname": "custom_contact_person", "label": "联系人", "required": False},
    {"fieldname": "custom_phone", "label": "联系电话", "required": False},
    {"fieldname": "custom_address_text", "label": "地址", "required": False},
    {"fieldname": "custom_bank_info", "label": "银行账户信息", "required": False},
    {"fieldname": "custom_remark", "label": "备注", "required": False},
]


@frappe.whitelist()
def get_import_template(doctype):
    """Return column headers for the given doctype import template."""
    columns_map = {
        "Item": ITEM_IMPORT_COLUMNS,
        "Customer": CUSTOMER_IMPORT_COLUMNS,
        "Supplier": SUPPLIER_IMPORT_COLUMNS,
    }
    columns = columns_map.get(doctype)
    if not columns:
        frappe.throw(_("Unsupported doctype for import: {0}").format(doctype))
    return columns


@frappe.whitelist()
def validate_import_data(doctype, rows):
    """Validate import data before actual import. Returns list of errors."""
    import json

    if isinstance(rows, str):
        rows = json.loads(rows)

    columns_map = {
        "Item": ITEM_IMPORT_COLUMNS,
        "Customer": CUSTOMER_IMPORT_COLUMNS,
        "Supplier": SUPPLIER_IMPORT_COLUMNS,
    }
    columns = columns_map.get(doctype)
    if not columns:
        return [{"row": 0, "error": f"Unsupported doctype: {doctype}"}]

    required_fields = [c["fieldname"] for c in columns if c["required"]]
    errors = []

    for idx, row in enumerate(rows, start=2):
        for field in required_fields:
            if not row.get(field):
                label = next(c["label"] for c in columns if c["fieldname"] == field)
                errors.append({"row": idx, "field": field, "error": f"必填字段 [{label}] 为空"})

        if doctype == "Item" and row.get("item_code"):
            if frappe.db.exists("Item", row["item_code"]):
                errors.append(
                    {"row": idx, "field": "item_code", "error": f"商品编码 [{row['item_code']}] 已存在"}
                )

        if doctype == "Customer" and row.get("customer_name"):
            if frappe.db.exists("Customer", {"customer_name": row["customer_name"]}):
                errors.append(
                    {"row": idx, "field": "customer_name", "error": f"客户 [{row['customer_name']}] 已存在"}
                )

        if doctype == "Supplier" and row.get("supplier_name"):
            if frappe.db.exists("Supplier", {"supplier_name": row["supplier_name"]}):
                errors.append(
                    {"row": idx, "field": "supplier_name", "error": f"供应商 [{row['supplier_name']}] 已存在"}
                )

    return errors


@frappe.whitelist()
def import_records(doctype, rows):
    """Import validated records. Returns success/failure counts."""
    import json

    if isinstance(rows, str):
        rows = json.loads(rows)

    success = 0
    failed = 0
    errors = []

    for idx, row in enumerate(rows, start=2):
        try:
            if doctype == "Item":
                _import_item(row)
            elif doctype == "Customer":
                _import_customer(row)
            elif doctype == "Supplier":
                _import_supplier(row)
            else:
                frappe.throw(_("Unsupported doctype"))
            success += 1
        except Exception as e:
            failed += 1
            errors.append({"row": idx, "error": str(e)})

    frappe.db.commit()
    return {"success": success, "failed": failed, "errors": errors}


def _import_item(row):
    doc = frappe.new_doc("Item")
    doc.item_code = row.get("item_code")
    doc.item_name = row.get("item_name")
    doc.item_group = row.get("item_group", "All Item Groups")
    doc.stock_uom = row.get("stock_uom", "Nos")
    doc.is_stock_item = 1
    doc.include_item_in_manufacturing = 1

    if row.get("custom_specification"):
        doc.custom_specification = row["custom_specification"]
    if row.get("standard_rate"):
        doc.standard_rate = float(row["standard_rate"])
    if row.get("custom_purchase_price"):
        doc.custom_purchase_price = float(row["custom_purchase_price"])
    if row.get("custom_supplier_ref"):
        doc.custom_supplier_ref = row["custom_supplier_ref"]
    if row.get("safety_stock"):
        doc.safety_stock = float(row["safety_stock"])
    if row.get("custom_min_stock_qty"):
        doc.custom_min_stock_qty = float(row["custom_min_stock_qty"])
    if row.get("description"):
        doc.description = row["description"]

    doc.insert(ignore_permissions=True)


def _import_customer(row):
    doc = frappe.new_doc("Customer")
    doc.customer_name = row.get("customer_name")
    doc.customer_group = row.get("customer_group", "All Customer Groups")

    if row.get("custom_contact_person"):
        doc.custom_contact_person = row["custom_contact_person"]
    if row.get("custom_phone"):
        doc.custom_phone = row["custom_phone"]
    if row.get("custom_address_text"):
        doc.custom_address_text = row["custom_address_text"]
    if row.get("custom_remark"):
        doc.custom_remark = row["custom_remark"]

    doc.insert(ignore_permissions=True)


def _import_supplier(row):
    doc = frappe.new_doc("Supplier")
    doc.supplier_name = row.get("supplier_name")
    doc.supplier_group = row.get("supplier_group", "All Supplier Groups")

    if row.get("custom_contact_person"):
        doc.custom_contact_person = row["custom_contact_person"]
    if row.get("custom_phone"):
        doc.custom_phone = row["custom_phone"]
    if row.get("custom_address_text"):
        doc.custom_address_text = row["custom_address_text"]
    if row.get("custom_bank_info"):
        doc.custom_bank_info = row["custom_bank_info"]
    if row.get("custom_remark"):
        doc.custom_remark = row["custom_remark"]

    doc.insert(ignore_permissions=True)
