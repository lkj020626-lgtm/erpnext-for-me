#!/bin/bash
# StarMake ERP - CentOS/Rocky Linux 服务器初始化脚本
# 功能：安装 Docker + Docker Compose，配置防火墙，设置开机自启
# 支持：CentOS 7/8/Stream, Rocky Linux 8/9, AlmaLinux 8/9

set -e

echo "========================================="
echo "  星造 StarMake ERP 服务器初始化"
echo "========================================="
echo ""

# 检测系统版本
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
    echo "检测到系统: $PRETTY_NAME"
else
    echo "无法检测系统版本，退出。"
    exit 1
fi

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 用户运行此脚本"
    exit 1
fi

echo ""
echo "[1/6] 安装基础依赖..."
yum install -y yum-utils device-mapper-persistent-data lvm2 curl wget git

echo ""
echo "[2/6] 添加 Docker 仓库..."
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

echo ""
echo "[3/6] 安装 Docker..."
yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo ""
echo "[4/6] 启动 Docker 并设置开机自启..."
systemctl start docker
systemctl enable docker

# 验证 Docker
docker --version
docker compose version

echo ""
echo "[5/6] 配置防火墙..."
if systemctl is-active --quiet firewalld; then
    firewall-cmd --permanent --add-port=80/tcp
    firewall-cmd --permanent --add-port=443/tcp
    firewall-cmd --reload
    echo "防火墙已放行 80/443 端口"
else
    echo "firewalld 未运行，跳过防火墙配置"
fi

echo ""
echo "[6/6] 创建部署目录..."
mkdir -p /opt/starmake
echo "部署目录: /opt/starmake"

# 设置 Docker 日志轮转（防止日志撑爆磁盘）
cat > /etc/docker/daemon.json <<EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    },
    "storage-driver": "overlay2"
}
EOF
systemctl restart docker

echo ""
echo "========================================="
echo "  服务器初始化完成！"
echo "========================================="
echo ""
echo "下一步："
echo "  1. 将 StarMake 部署文件上传到 /opt/starmake/"
echo "  2. cd /opt/starmake/deployment"
echo "  3. cp .env.example .env && 编辑 .env"
echo "  4. bash scripts/init.sh"
echo ""
echo "服务器信息："
echo "  IP 地址: $(hostname -I | awk '{print $1}')"
echo "  内存: $(free -h | awk '/Mem:/{print $2}')"
echo "  磁盘: $(df -h / | awk 'NR==2{print $4}') 可用"
