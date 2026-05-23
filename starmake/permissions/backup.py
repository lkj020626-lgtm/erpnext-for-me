"""
StarMake Data Backup Module

Supports:
- Automatic daily backup via scheduler
- Manual backup trigger
- Backup to local directory, USB drive, or NAS path
- 30-day retention policy
- Backup file naming by date
"""

import os
import shutil
from datetime import datetime, timedelta

import frappe
from frappe import _


DEFAULT_BACKUP_PATH = "/home/frappe/backups"
RETENTION_DAYS = 30


@frappe.whitelist()
def create_backup(backup_path=None):
    """Create a manual backup of the current site."""
    site_name = frappe.local.site
    backup_path = backup_path or _get_backup_path()

    os.makedirs(backup_path, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{site_name}_{date_str}"

    try:
        from frappe.utils.backups import new_backup

        backup = new_backup(
            ignore_files=False,
            backup_path_db=None,
            backup_path_files=None,
            backup_path_private_files=None,
            force=True,
        )

        db_path = backup.backup_path_db
        files_path = backup.backup_path_files
        private_path = backup.backup_path_private_files

        target_dir = os.path.join(backup_path, backup_filename)
        os.makedirs(target_dir, exist_ok=True)

        for src in [db_path, files_path, private_path]:
            if src and os.path.exists(src):
                shutil.copy2(src, target_dir)

        _cleanup_old_backups(backup_path)

        return {
            "success": True,
            "path": target_dir,
            "message": _("备份成功：{0}").format(target_dir),
        }
    except Exception as e:
        frappe.log_error(f"StarMake backup error: {e}", "StarMake Backup")
        return {"success": False, "message": str(e)}


def scheduled_backup():
    """Called by scheduler for daily automatic backup."""
    result = create_backup()
    if result["success"]:
        frappe.logger().info(f"StarMake daily backup completed: {result['path']}")
    else:
        frappe.logger().error(f"StarMake daily backup failed: {result['message']}")


def _get_backup_path():
    """Get configured backup path or default."""
    custom_path = frappe.db.get_single_value("System Settings", "backup_path") if frappe.db else None
    if custom_path and os.path.isdir(custom_path):
        return custom_path

    site_path = frappe.get_site_path()
    return os.path.join(site_path, "private", "backups", "starmake")


def _cleanup_old_backups(backup_path):
    """Remove backups older than RETENTION_DAYS."""
    if not os.path.exists(backup_path):
        return

    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)

    for entry in os.listdir(backup_path):
        entry_path = os.path.join(backup_path, entry)
        if not os.path.isdir(entry_path):
            continue

        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(entry_path))
            if mtime < cutoff:
                shutil.rmtree(entry_path)
                frappe.logger().info(f"StarMake: removed old backup {entry_path}")
        except (OSError, ValueError):
            continue


@frappe.whitelist()
def get_backup_list(backup_path=None):
    """List available backups."""
    backup_path = backup_path or _get_backup_path()

    if not os.path.exists(backup_path):
        return []

    backups = []
    for entry in sorted(os.listdir(backup_path), reverse=True):
        entry_path = os.path.join(backup_path, entry)
        if os.path.isdir(entry_path):
            size = sum(
                os.path.getsize(os.path.join(entry_path, f))
                for f in os.listdir(entry_path)
                if os.path.isfile(os.path.join(entry_path, f))
            )
            mtime = datetime.fromtimestamp(os.path.getmtime(entry_path))
            backups.append(
                {
                    "name": entry,
                    "path": entry_path,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "date": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

    return backups


@frappe.whitelist()
def configure_backup_path(path):
    """Set custom backup path (local dir, NAS mount, USB)."""
    if not os.path.isdir(path):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            frappe.throw(_("无法创建备份目录：{0}").format(str(e)))

    if not os.access(path, os.W_OK):
        frappe.throw(_("备份目录无写入权限：{0}").format(path))

    frappe.db.set_single_value("System Settings", "backup_path", path)
    frappe.db.commit()
    return {"success": True, "message": _("备份路径已设置为：{0}").format(path)}
