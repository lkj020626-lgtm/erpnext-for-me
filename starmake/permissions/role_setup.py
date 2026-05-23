import frappe


ROLE_PERMISSIONS = {
    "工厂老板": {
        "full_access": [
            "Item", "Customer", "Supplier", "Warehouse",
            "Purchase Order", "Purchase Receipt",
            "Sales Order", "Delivery Note",
            "Stock Entry", "Stock Reconciliation",
            "Work Order", "BOM",
        ],
        "report_access": True,
    },
    "采购员": {
        "full_access": ["Purchase Order", "Purchase Receipt", "Supplier"],
        "read_only": ["Item", "Warehouse"],
        "report_access": False,
    },
    "销售员": {
        "full_access": ["Sales Order", "Delivery Note", "Customer"],
        "read_only": ["Item", "Warehouse"],
        "report_access": False,
    },
    "仓管员": {
        "full_access": [
            "Purchase Receipt", "Delivery Note", "Stock Entry",
            "Stock Reconciliation", "Warehouse",
        ],
        "read_only": ["Item", "Purchase Order", "Sales Order", "Work Order"],
        "report_access": False,
    },
    "生产主管": {
        "full_access": ["Work Order", "BOM", "Stock Entry"],
        "read_only": ["Item", "Warehouse"],
        "report_access": False,
    },
}


def setup_roles():
    """Create roles and assign permissions after install."""
    for role_name, perms in ROLE_PERMISSIONS.items():
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert(
                ignore_permissions=True
            )

        for doctype in perms.get("full_access", []):
            _add_permission(doctype, role_name, read=1, write=1, create=1, delete=0, submit=1, cancel=1)

        for doctype in perms.get("read_only", []):
            _add_permission(doctype, role_name, read=1, write=0, create=0, delete=0, submit=0, cancel=0)

    frappe.db.commit()


def _add_permission(doctype, role, read=1, write=0, create=0, delete=0, submit=0, cancel=0):
    """Add or update a permission rule."""
    existing = frappe.db.exists(
        "Custom DocPerm",
        {"parent": doctype, "role": role, "permlevel": 0},
    )

    if existing:
        return

    try:
        from frappe.permissions import add_permission

        add_permission(doctype, role, permlevel=0)
        frappe.db.set_value(
            "Custom DocPerm",
            {"parent": doctype, "role": role, "permlevel": 0},
            {
                "read": read,
                "write": write,
                "create": create,
                "delete": delete,
                "submit": submit,
                "cancel": cancel,
            },
        )
    except Exception:
        pass
