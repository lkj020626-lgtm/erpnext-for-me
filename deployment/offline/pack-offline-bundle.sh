#!/bin/bash
# StarMake 离线部署包打包脚本
# 在能翻墙的机器上运行，生成离线安装包，拷贝到目标服务器
#
# 前提：本机已安装 Docker
# 产出：starmake-offline-bundle.tar.gz（约 2-3 GB）

set -e

BUNDLE_DIR="./starmake-offline-bundle"
echo "========================================="
echo "  StarMake 离线部署包打包"
echo "========================================="

rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR"/{images,scripts,app}

echo ""
echo "[1/5] 拉取所需 Docker 镜像..."
docker pull mariadb:10.11
docker pull redis:7-alpine
docker pull nginx:alpine
docker pull frappe/bench:latest

echo ""
echo "[2/5] 导出镜像为 tar 文件..."
docker save mariadb:10.11 -o "$BUNDLE_DIR/images/mariadb.tar"
docker save redis:7-alpine -o "$BUNDLE_DIR/images/redis.tar"
docker save nginx:alpine -o "$BUNDLE_DIR/images/nginx.tar"
docker save frappe/bench:latest -o "$BUNDLE_DIR/images/frappe-bench.tar"

echo ""
echo "[3/5] 复制应用代码..."
# 假设当前在 starmake 仓库根目录
cp -r ../starmake "$BUNDLE_DIR/app/" 2>/dev/null || cp -r . "$BUNDLE_DIR/app/"

echo ""
echo "[4/5] 生成离线安装脚本..."
cat > "$BUNDLE_DIR/install-offline.sh" << 'INSTALL_EOF'
#!/bin/bash
# StarMake 离线安装脚本 - 在目标服务器上运行
set -e

echo "========================================="
echo "  StarMake ERP 离线安装"
echo "========================================="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "[!] Docker 未安装。"
    echo "    如果服务器完全无网络，请先用 deb 包离线安装 Docker。"
    echo "    如果有国内网络，运行："
    echo "    curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg"
    echo "    echo 'deb [signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.aliyun.com/docker-ce/linux/debian bookworm stable' | sudo tee /etc/apt/sources.list.d/docker.list"
    echo "    sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin"
    exit 1
fi

echo ""
echo "[1/4] 导入 Docker 镜像..."
for img in "$SCRIPT_DIR"/images/*.tar; do
    echo "  加载: $(basename $img)"
    docker load -i "$img"
done

echo ""
echo "[2/4] 复制应用到 /opt/starmake..."
sudo mkdir -p /opt/starmake
sudo cp -r "$SCRIPT_DIR"/app/* /opt/starmake/
sudo chown -R $USER:$USER /opt/starmake

echo ""
echo "[3/4] 配置环境..."
cd /opt/starmake/deployment
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[!] 请编辑 /opt/starmake/deployment/.env 设置密码"
    echo "    然后运行: cd /opt/starmake/deployment && bash scripts/init.sh"
    exit 0
fi

echo ""
echo "[4/4] 启动服务..."
bash scripts/init.sh

echo ""
echo "========================================="
echo "  离线安装完成！"
echo "========================================="
INSTALL_EOF
chmod +x "$BUNDLE_DIR/install-offline.sh"

echo ""
echo "[5/5] 打包..."
tar -czf starmake-offline-bundle.tar.gz -C "$(dirname $BUNDLE_DIR)" "$(basename $BUNDLE_DIR)"
rm -rf "$BUNDLE_DIR"

SIZE=$(du -h starmake-offline-bundle.tar.gz | cut -f1)
echo ""
echo "========================================="
echo "  打包完成！"
echo "  文件: starmake-offline-bundle.tar.gz ($SIZE)"
echo "========================================="
echo ""
echo "使用方法："
echo "  1. 将 starmake-offline-bundle.tar.gz 拷贝到目标服务器"
echo "  2. tar -xzf starmake-offline-bundle.tar.gz"
echo "  3. cd starmake-offline-bundle"
echo "  4. sudo bash install-offline.sh"
