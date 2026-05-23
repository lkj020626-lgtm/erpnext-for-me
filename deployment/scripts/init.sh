#!/bin/bash
# StarMake ERP 初始化脚本
# 首次部署时运行此脚本

set -e

echo "========================================="
echo "  星造 StarMake ERP 初始化部署"
echo "========================================="

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "[!] 未找到 .env 文件，从模板创建..."
    cp .env.example .env
    echo "[!] 请编辑 .env 文件设置密码后重新运行此脚本"
    exit 1
fi

source .env

# 创建备份目录
mkdir -p ${BACKUP_PATH:-./backups}

echo "[1/5] 构建 Docker 镜像..."
docker compose build

echo "[2/5] 启动数据库和 Redis..."
docker compose up -d mariadb redis-cache redis-queue
echo "等待数据库就绪..."
sleep 15

echo "[3/5] 启动应用容器..."
docker compose up -d starmake-app

echo "等待应用就绪..."
sleep 10

echo "[4/5] 创建站点并安装应用..."
docker exec starmake-app bash -c "
    cd /home/frappe/frappe-bench
    bench new-site ${SITE_NAME} \
        --db-root-password ${MYSQL_ROOT_PASSWORD} \
        --admin-password ${ADMIN_PASSWORD} \
        --db-name ${DB_NAME} \
        --no-mariadb-socket
    bench --site ${SITE_NAME} install-app erpnext
    bench --site ${SITE_NAME} install-app starmake
    bench --site ${SITE_NAME} migrate
    bench --site ${SITE_NAME} set-config server_script_enabled 1
    echo '${SITE_NAME}' > sites/currentsite.txt
"

echo "[5/5] 启动所有服务..."
docker compose up -d

echo ""
echo "========================================="
echo "  部署完成！"
echo "  访问地址: http://${SITE_NAME}"
echo "  管理员账号: Administrator"
echo "  管理员密码: ${ADMIN_PASSWORD}"
echo "========================================="
echo ""
echo "提示："
echo "  - 如果用 IP 访问，请将 SITE_NAME 设为服务器 IP"
echo "  - 首次登录后请立即修改管理员密码"
echo "  - 备份文件存放在: ${BACKUP_PATH:-./backups}"
