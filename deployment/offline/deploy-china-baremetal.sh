#!/bin/bash
# StarMake - 裸机部署（国内网络版）
# 适用于 Debian 12/13，服务器有国内网络但无法翻墙
# 使用国内镜像源完成所有安装

set -e

echo "========================================="
echo "  StarMake ERP 裸机部署（国内网络）"
echo "========================================="

# 检查 root
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 运行"
    exit 1
fi

# 配置国内 APT 源
echo "[1/9] 配置 APT 源..."
cp /etc/apt/sources.list /etc/apt/sources.list.bak 2>/dev/null || true
cat > /etc/apt/sources.list << 'EOF'
deb https://mirrors.aliyun.com/debian/ bookworm main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free non-free-firmware
EOF
apt update

echo "[2/9] 安装系统依赖..."
apt install -y \
    git python3 python3-dev python3-pip python3-venv \
    mariadb-server mariadb-client \
    redis-server \
    curl wget sudo \
    xvfb libfontconfig wkhtmltopdf \
    fonts-wqy-zenhei fonts-wqy-microhei \
    nginx supervisor cron

# 安装 Node.js（使用 npmmirror）
echo "[3/9] 安装 Node.js..."
curl -fsSL https://npmmirror.com/mirrors/node/latest-v18.x/SHASUMS256.txt > /dev/null 2>&1 || true
curl -fsSL https://deb.nodesource.com/setup_18.x | bash - || {
    # 如果 nodesource 不通，用 npmmirror
    NODE_VER="18.20.4"
    wget -q "https://npmmirror.com/mirrors/node/v${NODE_VER}/node-v${NODE_VER}-linux-x64.tar.xz" -O /tmp/node.tar.xz
    tar -xf /tmp/node.tar.xz -C /usr/local --strip-components=1
    rm /tmp/node.tar.xz
}
apt install -y nodejs 2>/dev/null || true
npm config set registry https://registry.npmmirror.com
npm install -g yarn
yarn config set registry https://registry.npmmirror.com

# 配置 MariaDB
echo "[4/9] 配置 MariaDB..."
cat >> /etc/mysql/mariadb.conf.d/50-server.cnf << 'EOF'

[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
innodb_buffer_pool_size = 256M
max_allowed_packet = 256M

[mysql]
default-character-set = utf8mb4
EOF
systemctl restart mariadb

# 设置 MariaDB root 密码
MYSQL_ROOT_PASS="StArMaKe2024!"
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${MYSQL_ROOT_PASS}'; FLUSH PRIVILEGES;" 2>/dev/null || true

# 创建 frappe 用户
echo "[5/9] 创建 frappe 用户..."
id frappe &>/dev/null || adduser --disabled-password --gecos "" frappe
echo "frappe ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/frappe

# 配置 pip 镜像
echo "[6/9] 配置 pip 镜像..."
sudo -u frappe mkdir -p /home/frappe/.pip
cat > /home/frappe/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
chown frappe:frappe /home/frappe/.pip/pip.conf

# 安装 bench
echo "[7/9] 安装 Frappe Bench..."
sudo -u frappe pip3 install frappe-bench --break-system-packages 2>/dev/null || \
sudo -u frappe pip3 install frappe-bench

# 初始化 bench 和安装应用
echo "[8/9] 初始化 bench 并安装 ERPNext..."
sudo -u frappe bash << 'FRAPPE_EOF'
cd /home/frappe
export PATH=$PATH:/home/frappe/.local/bin

bench init frappe-bench --frappe-branch version-15
cd frappe-bench

bench get-app erpnext --branch version-15

# 安装 StarMake
bench get-app https://gitee.com/mirrors/erpnext-for-me.git 2>/dev/null || \
bench get-app https://github.com/lkj020626-lgtm/erpnext-for-me.git 2>/dev/null || \
echo "[!] 无法从远程获取 StarMake，请手动复制到 apps/ 目录"

FRAPPE_EOF

# 创建站点
echo "[9/9] 创建站点..."
ADMIN_PASS="admin123"
sudo -u frappe bash << SITE_EOF
cd /home/frappe/frappe-bench
export PATH=\$PATH:/home/frappe/.local/bin

bench new-site erp.local \
    --db-root-password ${MYSQL_ROOT_PASS} \
    --admin-password ${ADMIN_PASS} \
    --db-name starmake_db

bench --site erp.local install-app erpnext
bench --site erp.local install-app starmake 2>/dev/null || echo "[!] StarMake 未安装，请手动安装"
bench --site erp.local migrate

echo "erp.local" > sites/currentsite.txt
SITE_EOF

# 配置生产模式
sudo -u frappe bash -c "cd /home/frappe/frappe-bench && export PATH=\$PATH:/home/frappe/.local/bin && sudo bench setup production frappe"

echo ""
echo "========================================="
echo "  部署完成！"
echo "========================================="
echo ""
echo "  访问地址: http://$(hostname -I | awk '{print $1}')"
echo "  管理员: Administrator"
echo "  密码: ${ADMIN_PASS}"
echo ""
echo "  MariaDB root 密码: ${MYSQL_ROOT_PASS}"
echo "  请登录后立即修改管理员密码！"
