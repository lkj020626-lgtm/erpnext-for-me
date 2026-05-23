#!/bin/bash
# StarMake ERP 运维工具箱
# 用法: ./manage.sh [命令]

set -e

case "$1" in
    start)
        echo "启动所有服务..."
        docker compose up -d
        echo "完成。"
        ;;
    stop)
        echo "停止所有服务..."
        docker compose stop
        echo "完成。"
        ;;
    restart)
        echo "重启所有服务..."
        docker compose restart
        echo "完成。"
        ;;
    status)
        echo "服务状态："
        docker compose ps
        ;;
    logs)
        # 查看日志，默认最近100行
        LINES=${2:-100}
        docker compose logs --tail=$LINES -f starmake-app
        ;;
    backup)
        echo "执行手动备份..."
        docker exec starmake-app bench --site $(cat .env | grep SITE_NAME | cut -d= -f2) execute starmake.permissions.backup.create_backup
        echo "备份完成。"
        ;;
    backup-list)
        echo "备份列表："
        ls -lht ${BACKUP_PATH:-./backups}/ 2>/dev/null || echo "暂无备份"
        ;;
    restore)
        if [ -z "$2" ]; then
            echo "用法: ./manage.sh restore <备份目录名>"
            echo "可用备份："
            ls ${BACKUP_PATH:-./backups}/ 2>/dev/null || echo "暂无备份"
            exit 1
        fi
        BACKUP_DIR="${BACKUP_PATH:-./backups}/$2"
        if [ ! -d "$BACKUP_DIR" ]; then
            echo "错误：备份目录不存在: $BACKUP_DIR"
            exit 1
        fi
        DB_FILE=$(ls "$BACKUP_DIR"/*database* 2>/dev/null | head -1)
        if [ -z "$DB_FILE" ]; then
            echo "错误：未找到数据库备份文件"
            exit 1
        fi
        echo "警告：恢复操作将覆盖当前数据！"
        read -p "确认恢复? (yes/no): " CONFIRM
        if [ "$CONFIRM" != "yes" ]; then
            echo "已取消。"
            exit 0
        fi
        source .env
        echo "正在恢复..."
        docker cp "$DB_FILE" starmake-app:/tmp/restore.sql.gz
        docker exec starmake-app bench --site ${SITE_NAME} restore /tmp/restore.sql.gz
        docker exec starmake-app bench --site ${SITE_NAME} migrate
        docker exec starmake-app bench --site ${SITE_NAME} clear-cache
        echo "恢复完成。"
        ;;
    update)
        echo "更新 StarMake 应用..."
        docker compose stop starmake-app scheduler worker-short worker-long
        docker compose build starmake-app
        docker compose up -d starmake-app
        docker exec starmake-app bench --site $(cat .env | grep SITE_NAME | cut -d= -f2) migrate
        docker compose up -d
        echo "更新完成。"
        ;;
    console)
        source .env
        docker exec -it starmake-app bench --site ${SITE_NAME} console
        ;;
    shell)
        docker exec -it starmake-app bash
        ;;
    *)
        echo "星造 StarMake ERP 运维工具"
        echo ""
        echo "用法: ./manage.sh <命令>"
        echo ""
        echo "可用命令："
        echo "  start       启动所有服务"
        echo "  stop        停止所有服务"
        echo "  restart     重启所有服务"
        echo "  status      查看服务状态"
        echo "  logs [行数] 查看应用日志（默认100行）"
        echo "  backup      执行手动备份"
        echo "  backup-list 查看备份列表"
        echo "  restore <名> 从备份恢复"
        echo "  update      更新 StarMake 应用"
        echo "  console     进入 Frappe 控制台"
        echo "  shell       进入容器终端"
        ;;
esac
