#!/bin/bash
# StarMake - 配置国内镜像源
# 适用于：服务器有国内网络但无法翻墙
# 在目标服务器上运行

set -e

echo "========================================="
echo "  配置国内镜像源"
echo "========================================="

# 1. 配置 APT 源（Debian）
echo ""
echo "[1/5] 配置 APT 镜像（阿里云）..."
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak 2>/dev/null || true
sudo tee /etc/apt/sources.list > /dev/null << 'EOF'
deb https://mirrors.aliyun.com/debian/ bookworm main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free non-free-firmware
EOF
sudo apt update

# 2. 配置 Docker 镜像源
echo ""
echo "[2/5] 配置 Docker 镜像加速..."
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
    "registry-mirrors": [
        "https://docker.1ms.run",
        "https://docker.xuanyuan.me",
        "https://docker.rainbond.cc"
    ],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    }
}
EOF
sudo systemctl restart docker 2>/dev/null || true

# 3. 配置 pip 镜像
echo ""
echo "[3/5] 配置 pip 镜像（清华）..."
mkdir -p ~/.pip
tee ~/.pip/pip.conf > /dev/null << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

# 4. 配置 npm 镜像
echo ""
echo "[4/5] 配置 npm 镜像（淘宝）..."
npm config set registry https://registry.npmmirror.com 2>/dev/null || true

# 5. 配置 Docker CE 安装源（阿里云）
echo ""
echo "[5/5] 配置 Docker CE 安装源..."
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg 2>/dev/null || true
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.aliyun.com/docker-ce/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update

echo ""
echo "========================================="
echo "  镜像源配置完成！"
echo "========================================="
echo ""
echo "现在可以正常安装 Docker 和拉取镜像了："
echo "  sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin"
