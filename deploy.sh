#!/bin/bash
set -e

INSTALL_DIR="/opt/sing-box-monitor"

echo "=== Sing-Box 延迟监控 部署 ==="

mkdir -p "$INSTALL_DIR/templates"

echo "[1/4] 创建 Python 虚拟环境..."
cd "$INSTALL_DIR"
python3 -m venv venv

echo "[2/4] 安装依赖..."
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q

echo "[3/4] 配置 systemd 服务..."
cp sing-box-monitor.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable sing-box-monitor

echo "[4/4] 启动服务..."
systemctl restart sing-box-monitor

echo ""
echo "=== 部署完成 ==="
echo "请确认 config.ini 中的 api_url 指向 sing-box 设备地址"
echo "访问 http://<本机IP>:8080 查看监控"
echo ""
echo "常用命令："
echo "  查看状态: systemctl status sing-box-monitor"
echo "  查看日志: journalctl -u sing-box-monitor -f"
echo "  重启服务: systemctl restart sing-box-monitor"
