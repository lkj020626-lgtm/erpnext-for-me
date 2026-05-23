app_name = "starmake"
app_title = "星造 StarMake"
app_publisher = "StarMake"
app_description = "Lightweight ERP for small manufacturers"
app_email = "dev@starmake.local"
app_license = "GNU General Public License (v3)"
app_icon = "octicon octicon-package"
app_color = "#2196F3"

develop_version = "0.x.x-develop"

app_include_js = ["/assets/starmake/js/starmake.js"]
app_include_css = ["/assets/starmake/css/starmake.css"]

# Fixtures - export Custom Fields, Property Setters, Client Scripts etc.
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "Master Data"]],
    },
    {
        "dt": "Property Setter",
        "filters": [["module", "=", "Master Data"]],
    },
    {
        "dt": "Client Script",
        "filters": [["module", "=", "Master Data"]],
    },
]

# DocType overrides via hooks
override_doctype_class = {}

# Whitelisted methods accessible from frontend
override_whitelisted_methods = {
    "starmake.master_data.import_export.get_import_template": "starmake.master_data.import_export.get_import_template",
    "starmake.master_data.import_export.validate_import_data": "starmake.master_data.import_export.validate_import_data",
    "starmake.master_data.import_export.import_records": "starmake.master_data.import_export.import_records",
    "starmake.master_data.excel_template.download_template": "starmake.master_data.excel_template.download_template",
}

# Document Events
doc_events = {
    "Purchase Order": {
        "validate": "starmake.buying.purchase_hooks.validate_purchase_order",
        "on_submit": "starmake.buying.purchase_hooks.on_submit_purchase_order",
    },
    "Purchase Receipt": {
        "validate": "starmake.buying.purchase_hooks.validate_purchase_receipt",
        "on_submit": "starmake.buying.purchase_hooks.on_submit_purchase_receipt",
    },
    "Sales Order": {
        "validate": "starmake.selling.sales_hooks.validate_sales_order",
        "on_submit": "starmake.selling.sales_hooks.on_submit_sales_order",
    },
    "Delivery Note": {
        "validate": "starmake.selling.sales_hooks.validate_delivery_note",
        "on_submit": "starmake.selling.sales_hooks.on_submit_delivery_note",
    },
    "Work Order": {
        "validate": "starmake.manufacturing.production_hooks.validate_work_order",
        "on_submit": "starmake.manufacturing.production_hooks.on_submit_work_order",
    },
    "Stock Entry": {
        "validate": "starmake.stock.stock_hooks.validate_stock_entry",
        "on_submit": "starmake.stock.stock_hooks.on_submit_stock_entry",
    },
    "Sales Invoice": {
        "on_submit": "starmake.finance.finance_hooks.on_submit_sales_invoice",
    },
    "Purchase Invoice": {
        "on_submit": "starmake.finance.finance_hooks.on_submit_purchase_invoice",
    },
    "Payment Entry": {
        "on_submit": "starmake.finance.finance_hooks.on_submit_payment_entry",
    },
    "Issue": {
        "on_update": "starmake.crm.crm_hooks.on_issue_update",
    },
}

# Scheduled Tasks
scheduler_events = {
    "daily_long": [
        "starmake.permissions.backup.scheduled_backup",
    ],
}

# Jinja template extensions
jinja = {}

# Installation hooks
after_install = "starmake.install.after_install"
after_migrate = "starmake.install.after_migrate"
