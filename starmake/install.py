import json
import os

import frappe


def after_install():
    import_fixtures()
    import_print_formats()
    _setup_roles()
    _setup_chinese()


def after_migrate():
    import_fixtures()
    import_print_formats()
    _setup_roles()


def _setup_chinese():
    from starmake.setup_wizard import setup_chinese_defaults, setup_simplified_desktop
    setup_chinese_defaults()
    setup_simplified_desktop()


def _setup_roles():
    from starmake.permissions.role_setup import setup_roles
    setup_roles()


def import_fixtures():
    fixtures_path = os.path.join(os.path.dirname(__file__), "fixtures")
    if not os.path.exists(fixtures_path):
        return

    for filename in sorted(os.listdir(fixtures_path)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(fixtures_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            records = json.load(f)

        for record in records:
            doctype = record.get("doctype")
            if not doctype:
                continue

            try:
                if doctype == "Custom Field":
                    _import_custom_field(record)
                elif doctype == "Property Setter":
                    _import_property_setter(record)
                else:
                    _import_generic(record)
            except Exception as e:
                frappe.log_error(
                    f"StarMake fixture import error: {filename} - {e}",
                    "StarMake Install",
                )

    frappe.db.commit()


def _import_custom_field(record):
    name = f"{record['dt']}-{record['fieldname']}"
    if frappe.db.exists("Custom Field", name):
        doc = frappe.get_doc("Custom Field", name)
        doc.update(record)
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc(record)
        doc.insert(ignore_permissions=True)


def _import_property_setter(record):
    filters = {
        "doc_type": record["doc_type"],
        "field_name": record["field_name"],
        "property": record["property"],
    }
    if frappe.db.exists("Property Setter", filters):
        name = frappe.db.get_value("Property Setter", filters)
        doc = frappe.get_doc("Property Setter", name)
        doc.value = record["value"]
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc(record)
        doc.insert(ignore_permissions=True)


def _import_generic(record):
    doctype = record["doctype"]
    if "name" in record and frappe.db.exists(doctype, record["name"]):
        doc = frappe.get_doc(doctype, record["name"])
        doc.update(record)
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc(record)
        doc.insert(ignore_permissions=True)


PRINT_FORMAT_MAP = {
    "StarMake Purchase Order": "purchase_order.html",
    "StarMake Purchase Receipt": "purchase_receipt.html",
    "StarMake Sales Order": "sales_order.html",
    "StarMake Delivery Note": "delivery_note.html",
    "StarMake Work Order": "work_order.html",
    "StarMake Stock Entry": "stock_entry.html",
    "StarMake Item Label": "item_label.html",
}


def import_print_formats():
    formats_path = os.path.join(os.path.dirname(__file__), "print_templates", "formats")
    fixtures_path = os.path.join(os.path.dirname(__file__), "fixtures", "print_format.json")

    if not os.path.exists(fixtures_path):
        return

    with open(fixtures_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    for record in records:
        name = record.get("name")
        html_file = PRINT_FORMAT_MAP.get(name)
        if html_file:
            html_path = os.path.join(formats_path, html_file)
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as hf:
                    record["html"] = hf.read()

        try:
            if frappe.db.exists("Print Format", name):
                doc = frappe.get_doc("Print Format", name)
                doc.html = record.get("html", "")
                doc.save(ignore_permissions=True)
            else:
                doc = frappe.get_doc(record)
                doc.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(
                f"StarMake print format import error: {name} - {e}",
                "StarMake Install",
            )

    frappe.db.commit()
