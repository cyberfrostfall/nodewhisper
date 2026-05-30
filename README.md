# nodewhisper

[中文](#中文) | [English](#english)

---

## 中文

一个轻量级的 sing-box 代理节点延迟监控工具。自动定时测试所有出站节点的延迟，并通过 Web 面板展示实时图表和历史数据。

### 功能特性

- 定时自动测试所有代理节点延迟
- 可视化 Web 面板，支持实时图表展示
- 节点健康报告（平均延迟、超时率、异常检测）
- SQLite 本地存储，数据自动清理
- 支持 systemd 部署为后台服务

### 环境要求

- Python 3.8 或更高版本
- 一台运行 sing-box 且开启了 Clash API 的设备（路由器、服务器等）
- 监控程序需要能访问到 sing-box 设备的 API 端口

### 安装步骤

#### 第一步：下载项目

```bash
# 克隆仓库到本地
git clone https://github.com/cyberfrostfall/nodewhisper.git

# 进入项目目录
cd nodewhisper
```

#### 第二步：创建 Python 虚拟环境（推荐）

```bash
# 创建虚拟环境
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
# 复制示例配置文件
cp config.ini.example config.ini

# 用你喜欢的编辑器打开配置文件
nano config.ini
```

配置文件说明：

```ini
[singbox]
# sing-box 设备的 API 地址（改成你自己的设备 IP 和端口）
api_url = http://192.168.2.200:9095

# Clash API 密钥（在 sing-box 配置中设置的 secret）
secret = 你的密钥

# 延迟测试目标网址（一般不需要改）
test_url = http://www.gstatic.com/generate_204

# 延迟超时时间，单位毫秒（超过此值视为超时）
timeout = 3000

[monitor]
# 检测间隔，单位分钟（每隔多久测一次延迟）
interval = 3

# 数据保留时长，单位小时（超过此时间的旧数据会被自动删除）
retention_hours = 24

# Web 面板监听端口
port = 8080
```

> **如何找到你的 sing-box API 地址？**
>
> 在 sing-box 的配置文件中找到 `experimental.clash_api` 部分，例如：
> ```json
> "clash_api": {
>   "external_controller": "0.0.0.0:9095",
>   "secret": "你的密钥"
> }
> ```
> 其中 `external_controller` 的端口就是 API 端口，`secret` 就是密钥。

#### 第五步：运行

```bash
python app.py
```

启动后，打开浏览器访问 `http://localhost:8080` 即可看到监控面板。

如果你在远程服务器上运行，将 `localhost` 替换为服务器的 IP 地址。

### 部署为系统服务（可选）

如果你希望程序开机自启、后台常驻运行：

```bash
# 方式一：使用自动部署脚本
# 先把项目文件复制到 /opt/sing-box-monitor
sudo mkdir -p /opt/sing-box-monitor
sudo cp -r ./* /opt/sing-box-monitor/
sudo cp config.ini /opt/sing-box-monitor/

# 运行部署脚本
cd /opt/sing-box-monitor
sudo bash deploy.sh
```

```bash
# 方式二：手动部署
# 1. 复制服务文件
sudo cp sing-box-monitor.service /etc/systemd/system/

# 2. 重新加载 systemd
sudo systemctl daemon-reload

# 3. 启用并启动服务
sudo systemctl enable --now sing-box-monitor

# 4. 查看运行状态
sudo systemctl status sing-box-monitor
```

常用管理命令：

```bash
# 查看服务状态
sudo systemctl status sing-box-monitor

# 查看实时日志
sudo journalctl -u sing-box-monitor -f

# 重启服务
sudo systemctl restart sing-box-monitor

# 停止服务
sudo systemctl stop sing-box-monitor
```

### 常见问题

**Q: 启动后看不到任何节点数据？**

A: 检查 `config.ini` 中的 `api_url` 和 `secret` 是否正确。确保监控程序所在机器能访问到 sing-box 的 API 端口。可以用 `curl http://你的IP:端口/proxies` 测试连通性。

**Q: 如何修改检测频率？**

A: 编辑 `config.ini` 中的 `interval` 值（单位为分钟），修改后重启程序即可生效。

**Q: 数据库文件在哪里？**

A: 数据库文件 `data.db` 会自动生成在项目目录下。如需重置数据，删除该文件后重启程序即可。

---

## English

A lightweight sing-box proxy node delay monitor. It periodically tests latency for all outbound nodes and visualizes the results in a clean web dashboard.

### Features

- Automatic delay testing for all proxy nodes at configurable intervals
- Web dashboard with real-time latency charts
- Node health reports (average delay, timeout rate, anomaly detection)
- SQLite local storage with automatic data cleanup
- Systemd service file included for daemon deployment

### Requirements

- Python 3.8+
- A device running sing-box with Clash API enabled (router, server, etc.)
- Network access from the monitor to the sing-box API port

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
# sing-box device API address (use your device's IP and port)
api_url = http://192.168.2.200:9095

# Clash API secret (set in your sing-box config)
secret = your_secret_here

# Delay test target URL (usually no need to change)
test_url = http://www.gstatic.com/generate_204

# Delay timeout in milliseconds (nodes exceeding this are marked as timed out)
timeout = 3000

[monitor]
# Check interval in minutes (how often to test delays)
interval = 3

# Data retention in hours (older records are automatically deleted)
retention_hours = 24

# Web dashboard listen port
port = 8080
```

> **How to find your sing-box API address?**
>
> Look for the `experimental.clash_api` section in your sing-box config:
> ```json
> "clash_api": {
>   "external_controller": "0.0.0.0:9095",
>   "secret": "your_secret"
> }
> ```
> The port in `external_controller` is the API port, and `secret` is the API key.

#### Step 5: Run

```bash
python app.py
```

Open your browser and visit `http://localhost:8080` to see the dashboard.

If running on a remote server, replace `localhost` with the server's IP address.

### Deploy as a System Service (optional)

To run the monitor as a background service that starts on boot:

```bash
# Option 1: Use the deploy script
sudo mkdir -p /opt/sing-box-monitor
sudo cp -r ./* /opt/sing-box-monitor/
sudo cp config.ini /opt/sing-box-monitor/
cd /opt/sing-box-monitor
sudo bash deploy.sh
```

```bash
# Option 2: Manual deployment
sudo cp sing-box-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now sing-box-monitor
sudo systemctl status sing-box-monitor
```

Useful commands:

```bash
# Check service status
sudo systemctl status sing-box-monitor

# View live logs
sudo journalctl -u sing-box-monitor -f

# Restart service
sudo systemctl restart sing-box-monitor

# Stop service
sudo systemctl stop sing-box-monitor
```

### FAQ

**Q: No node data showing after startup?**

A: Verify `api_url` and `secret` in `config.ini`. Make sure the monitor can reach the sing-box API port. Test with `curl http://your-ip:port/proxies`.

**Q: How to change the check frequency?**

A: Edit the `interval` value in `config.ini` (in minutes), then restart the program.

**Q: Where is the database file?**

A: The database `data.db` is auto-created in the project directory. To reset data, delete the file and restart.

---

## License

MIT
