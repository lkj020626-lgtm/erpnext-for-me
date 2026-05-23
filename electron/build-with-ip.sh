#!/bin/bash
# ============================================================
# 星造 ERP 桌面客户端打包脚本
# 用法: bash build-with-ip.sh 192.168.1.100
# ============================================================

set -e

SERVER_IP="${1:-192.168.1.100}"
PROTOCOL="${2:-http}"
SERVER_URL="${PROTOCOL}://${SERVER_IP}"

echo "========================================="
echo "  星造 StarMake ERP 客户端打包"
echo "  服务器地址: ${SERVER_URL}"
echo "========================================="

# 写入服务器地址到配置
cat > server.json <<EOF
{
  "serverUrl": "${SERVER_URL}"
}
EOF

echo "[1/3] 安装依赖..."
npm install

echo "[2/3] 打包 Windows 安装包..."
npm run build:win

echo "[3/3] 完成！"
echo ""
echo "安装包位置: dist/"
ls -lh dist/*.exe 2>/dev/null || echo "（查看 dist/ 目录）"
echo ""
echo "分发方式："
echo "  1. 拷贝 .exe 到共享文件夹，员工自行安装"
echo "  2. 使用 deploy-lan.bat 批量推送到局域网电脑"
