#!/bin/bash
set -e

INSTALL_DIR="/opt/nodewhisper"

echo "=== NodeWhisper 部署 ==="

mkdir -p "$INSTALL_DIR/templates"
mkdir -p "$INSTALL_DIR/proto"
mkdir -p "$INSTALL_DIR/proto_gen"

echo "[1/5] 创建 Python 虚拟环境..."
cd "$INSTALL_DIR"
python3 -m venv venv

echo "[2/5] 安装依赖..."
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q

echo "[3/5] 生成 proto stubs..."
./venv/bin/pip install grpcio-tools -q
./venv/bin/python -m grpc_tools.protoc \
  -I./proto \
  --python_out=./proto_gen \
  --grpc_python_out=./proto_gen \
  proto/started_service.proto
sed -i 's/^import started_service_pb2/from . import started_service_pb2/' proto_gen/started_service_pb2_grpc.py
touch proto_gen/__init__.py

echo "[4/5] 配置 systemd 服务..."
cp nodewhisper.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable nodewhisper

echo "[5/5] 启动服务..."
systemctl restart nodewhisper

echo ""
echo "=== 部署完成 ==="
echo "请确认 config.ini 中的 api_url 指向 sing-box 设备的 gRPC API 地址 (host:port)"
echo "访问 http://<本机IP>:8080 查看监控"
echo ""
echo "常用命令："
echo "  查看状态: systemctl status nodewhisper"
echo "  查看日志: journalctl -u nodewhisper -f"
echo "  重启服务: systemctl restart nodewhisper"
