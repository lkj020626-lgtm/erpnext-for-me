"""
StarMake Project / Asset / HR Module
- Project implementation tracking
- Asset register
- Basic attendance and leave
"""

import frappe



@frappe.whitelist()
def get_project_dashboard():
    """Get project status overview."""
    return frappe.db.sql(
        """
        SELECT
            status,
            COUNT(*) as count,
            SUM(estimated_costing) as total_budget,
            AVG(percent_complete) as avg_progress
        FROM `tabProject`
        WHERE status != 'Cancelled'
        GROUP BY status
        ORDER BY FIELD(status, 'Open', 'Overdue', 'Completed')
        """,
        as_dict=True,
    )


@frappe.whitelist()
def get_asset_register(asset_category=None, location=None):
    """Get asset register for equipment tracking."""
    conditions = ["a.docstatus = 1"]
    params = {}

    if asset_category:
        conditions.append("a.asset_category = %(asset_category)s")
        params["asset_category"] = asset_category
    if location:
        conditions.append("a.location = %(location)s")
        params["location"] = location

    where_clause = " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            a.name, a.asset_name, a.asset_category,
            a.location, a.custodian, a.status,
            a.purchase_date, a.gross_purchase_amount,
            a.value_after_depreciation,
            a.maintenance_required_before
        FROM `tabAsset` a
        WHERE {where_clause}
        ORDER BY a.asset_category, a.asset_name
        """,
        params,
        as_dict=True,
    )


@frappe.whitelist()
def get_attendance_summary(employee=None, month=None, year=None):
    """Get attendance summary."""
    conditions = ["1=1"]
    params = {}

    if employee:
        conditions.append("attendance_date >= %(from_date)s")
        conditions.append("employee = %(employee)s")
        params["employee"] = employee
    if month and year:
        conditions.append("MONTH(attendance_date) = %(month)s")
        conditions.append("YEAR(attendance_date) = %(year)s")
        params["month"] = month
        params["year"] = year

    where_clause = " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            employee, employee_name,
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_days,
            SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent_days,
            SUM(CASE WHEN status = 'Half Day' THEN 1 ELSE 0 END) as half_days,
            SUM(CASE WHEN status = 'On Leave' THEN 1 ELSE 0 END) as leave_days,
            COUNT(*) as total_days
        FROM `tabAttendance`
        WHERE docstatus = 1 AND {where_clause}
        GROUP BY employee
        ORDER BY employee_name
        """,
        params,
        as_dict=True,
    )
