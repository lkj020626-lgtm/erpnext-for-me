"""
StarMake 站点初始化配置
- 设置默认语言为中文
- 简化桌面布局
- 配置新手友好的默认设置
"""

import frappe


def after_install():
    """Run after app installation to configure Chinese defaults."""
    from starmake.install import import_fixtures, import_print_formats, _setup_roles

    import_fixtures()
    import_print_formats()
    _setup_roles()
    setup_chinese_defaults()
    setup_simplified_desktop()


def setup_chinese_defaults():
    """Configure site for Chinese language and locale."""
    # Set system default language to Chinese
    frappe.db.set_single_value("System Settings", "language", "zh")
    frappe.db.set_single_value("System Settings", "date_format", "yyyy-mm-dd")
    frappe.db.set_single_value("System Settings", "time_format", "HH:mm:ss")
    frappe.db.set_single_value("System Settings", "number_format", "#,###.##")
    frappe.db.set_single_value("System Settings", "float_precision", "2")
    frappe.db.set_single_value("System Settings", "country", "China")
    frappe.db.set_single_value("System Settings", "time_zone", "Asia/Shanghai")

    # Set default language for Administrator
    frappe.db.set_value("User", "Administrator", "language", "zh")

    frappe.db.commit()


def setup_simplified_desktop():
    """Hide complex modules that small factories don't need initially."""
    modules_to_hide = [
        "Quality Management",
        "Projects",
        "EDI",
        "Subcontracting",
    ]

    for module_name in modules_to_hide:
        if frappe.db.exists("Module Def", module_name):
            frappe.db.set_value("Module Def", module_name, "app_name", "")

    frappe.db.commit()
