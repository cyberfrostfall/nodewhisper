# nodewhisper

[中文](#中文) | [English](#english)

---

## 中文

一个轻量级的 sing-box 代理节点延迟监控工具。通过 sing-box 原生 gRPC API 自动定时测试所有出站节点的延迟，并通过 Web 面板展示实时图表和历史数据。

### 功能特性

- 通过 sing-box 原生 API（gRPC）定时自动测试所有代理节点延迟
- 可视化 Web 面板，支持实时图表展示
- 节点健康报告（平均延迟、超时率、异常检测）
- SQLite 本地存储，数据自动清理
- 支持 systemd 部署为后台服务

### 环境要求

- Python 3.8 或更高版本
- 一台运行 sing-box 且开启了原生 API 服务的设备（路由器、服务器等）
- 监控程序需要能访问到 sing-box 设备的 API 端口

### sing-box 配置

在 sing-box 配置文件中启用原生 API 服务：

```json
{
  "services": [
    {
      "type": "api",
      "listen": "0.0.0.0",
      "listen_port": 9090,
      "access_control_allow_private_network": true
    }
  ]
}
```

如需认证，添加 `"secret": "你的密钥"` 字段。

### 安装步骤

#### 第一步：下载项目

```bash
git clone https://github.com/cyberfrostfall/nodewhisper.git
cd nodewhisper
```

#### 第二步：创建 Python 虚拟环境（推荐）

```bash
python3 -m venv venv

# 激活虚拟环境
# Linux / macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

#### 第三步：安装依赖

```bash
pip install -r requirements.txt
```

#### 第四步：配置

```bash
cp config.ini.example config.ini
nano config.ini
```

配置文件说明：

```ini
[singbox]
# sing-box 设备的 gRPC API 地址（host:port 格式）
api_url = 192.168.1.1:9090

# API 密钥（如果 sing-box 未设置 secret 则留空）
secret =

[monitor]
# 检测间隔，单位分钟
interval = 3

# 数据保留时长，单位小时
retention_hours = 24

# Web 面板监听端口
port = 8080
```

#### 第五步：运行

```bash
python app.py
```

启动后，打开浏览器访问 `http://localhost:8080` 即可看到监控面板。

### 部署为系统服务（可选）

```bash
sudo mkdir -p /opt/sing-box-monitor
sudo cp -r ./* /opt/sing-box-monitor/
sudo cp config.ini /opt/sing-box-monitor/
cd /opt/sing-box-monitor
sudo bash deploy.sh
```

常用管理命令：

```bash
sudo systemctl status sing-box-monitor
sudo journalctl -u sing-box-monitor -f
sudo systemctl restart sing-box-monitor
sudo systemctl stop sing-box-monitor
```

### 常见问题

**Q: 启动后看不到任何节点数据？**

A: 检查 `config.ini` 中的 `api_url` 是否正确指向 sing-box 的 API 端口。确保监控程序所在机器能访问到该端口。

**Q: 如何修改检测频率？**

A: 编辑 `config.ini` 中的 `interval` 值（单位为分钟），修改后重启程序即可生效。

**Q: 数据库文件在哪里？**

A: 数据库文件 `data.db` 会自动生成在项目目录下。如需重置数据，删除该文件后重启程序即可。

---

## English

A lightweight sing-box proxy node delay monitor. It connects to sing-box's native gRPC API to periodically test latency for all outbound nodes and visualizes the results in a clean web dashboard.

### Features

- Automatic delay testing via sing-box native API (gRPC)
- Web dashboard with real-time latency charts
- Node health reports (average delay, timeout rate, anomaly detection)
- SQLite local storage with automatic data cleanup
- Systemd service file included for daemon deployment

### Requirements

- Python 3.8+
- A device running sing-box with the native API service enabled (router, server, etc.)
- Network access from the monitor to the sing-box API port

### sing-box Configuration

Enable the native API service in your sing-box config:

```json
{
  "services": [
    {
      "type": "api",
      "listen": "0.0.0.0",
      "listen_port": 9090,
      "access_control_allow_private_network": true
    }
  ]
}
```

Add `"secret": "your_secret"` if you want authentication.

### Installation

#### Step 1: Clone the repository

```bash
git clone https://github.com/cyberfrostfall/nodewhisper.git
cd nodewhisper
```

#### Step 2: Create a Python virtual environment (recommended)

```bash
python3 -m venv venv

# Activate the virtual environment
# Linux / macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

#### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Configure

```bash
cp config.ini.example config.ini
nano config.ini
```

Configuration reference:

```ini
[singbox]
# sing-box gRPC API address (host:port format)
api_url = 192.168.1.1:9090

# API secret (leave empty if not set in sing-box)
secret =

[monitor]
# Check interval in minutes
interval = 3

# Data retention in hours
retention_hours = 24

# Web dashboard listen port
port = 8080
```

#### Step 5: Run

```bash
python app.py
```

Open your browser and visit `http://localhost:8080` to see the dashboard.

### Deploy as a System Service (optional)

```bash
sudo mkdir -p /opt/sing-box-monitor
sudo cp -r ./* /opt/sing-box-monitor/
sudo cp config.ini /opt/sing-box-monitor/
cd /opt/sing-box-monitor
sudo bash deploy.sh
```

Useful commands:

```bash
sudo systemctl status sing-box-monitor
sudo journalctl -u sing-box-monitor -f
sudo systemctl restart sing-box-monitor
sudo systemctl stop sing-box-monitor
```

### FAQ

**Q: No node data showing after startup?**

A: Verify `api_url` in `config.ini` points to the correct sing-box API port. Make sure the monitor can reach that port.

**Q: How to change the check frequency?**

A: Edit the `interval` value in `config.ini` (in minutes), then restart the program.

**Q: Where is the database file?**

A: The database `data.db` is auto-created in the project directory. To reset data, delete the file and restart.

---

## License

MIT
