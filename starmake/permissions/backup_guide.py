"""
StarMake 数据备份恢复指南
========================

1. 备份机制
-----------
- 系统每天自动执行一次完整备份（数据库 + 上传文件 + 私有文件）
- 备份文件按日期命名，存放在配置的备份目录中
- 自动保留最近 30 天的备份，超期自动清理
- 支持手动触发备份

2. 备份路径配置
--------------
默认路径: /home/frappe/backups 或 site/private/backups/starmake/
可通过 API 配置为：
- 本机其他目录
- 挂载的 NAS 路径（如 /mnt/nas/erp-backup/）
- USB 移动硬盘（如 /media/usb/erp-backup/）

配置方法:
    bench --site your-site console
    >>> from starmake.permissions.backup import configure_backup_path
    >>> configure_backup_path("/mnt/nas/erp-backup/")

3. 手动备份
-----------
方法一：通过 bench 命令
    bench --site your-site execute starmake.permissions.backup.create_backup

方法二：通过 API（需管理员权限）
    POST /api/method/starmake.permissions.backup.create_backup
    Body: {"backup_path": "/optional/custom/path"}

4. 恢复步骤
-----------
步骤 1: 找到要恢复的备份目录
    ls /home/frappe/backups/
    # 选择对应日期的目录，如 your-site_20260524_020000/

步骤 2: 恢复数据库
    bench --site your-site restore /path/to/backup/database.sql.gz

步骤 3: 恢复文件（如需要）
    # 解压 files_backup 到 site/public/files/
    # 解压 private_files_backup 到 site/private/files/

步骤 4: 执行迁移确保数据一致
    bench --site your-site migrate

步骤 5: 清除缓存
    bench --site your-site clear-cache

5. 恢复测试建议
--------------
建议每月执行一次恢复测试：
1. 在测试环境创建新 site
2. 用最新备份恢复
3. 验证数据完整性（检查商品数、订单数、库存数据）
4. 确认系统功能正常

6. Docker 环境特别说明
---------------------
如果使用 Docker 部署，备份目录需要挂载为 volume：
    volumes:
      - /host/path/backups:/home/frappe/backups

恢复时需要进入容器执行：
    docker exec -it <container> bash
    bench --site your-site restore /home/frappe/backups/xxx/database.sql.gz
"""
