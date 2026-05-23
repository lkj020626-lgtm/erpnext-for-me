import json

from frappe.tests.utils import FrappeTestCase

from starmake.master_data.import_export import (
    CUSTOMER_IMPORT_COLUMNS,
    ITEM_IMPORT_COLUMNS,
    SUPPLIER_IMPORT_COLUMNS,
    validate_import_data,
)


class TestImportExport(FrappeTestCase):
    def test_item_columns_defined(self):
        self.assertTrue(len(ITEM_IMPORT_COLUMNS) > 0)
        required = [c for c in ITEM_IMPORT_COLUMNS if c["required"]]
        self.assertGreaterEqual(len(required), 3)

    def test_customer_columns_defined(self):
        self.assertTrue(len(CUSTOMER_IMPORT_COLUMNS) > 0)

    def test_supplier_columns_defined(self):
        self.assertTrue(len(SUPPLIER_IMPORT_COLUMNS) > 0)

    def test_validate_empty_required_fields(self):
        rows = [{"item_code": "", "item_name": "", "item_group": "", "stock_uom": ""}]
        errors = validate_import_data("Item", json.dumps(rows))
        self.assertTrue(len(errors) > 0)
        field_names = [e["field"] for e in errors]
        self.assertIn("item_code", field_names)
        self.assertIn("item_name", field_names)

    def test_validate_valid_item(self):
        rows = [
            {
                "item_code": "TEST-STARMAKE-001",
                "item_name": "Test Item",
                "item_group": "All Item Groups",
                "stock_uom": "Nos",
            }
        ]
        errors = validate_import_data("Item", json.dumps(rows))
        non_dup_errors = [e for e in errors if "已存在" not in e.get("error", "")]
        self.assertEqual(len(non_dup_errors), 0)

    def test_validate_unsupported_doctype(self):
        errors = validate_import_data("Unknown", json.dumps([{}]))
        self.assertTrue(len(errors) > 0)
        self.assertIn("Unsupported", errors[0]["error"])
