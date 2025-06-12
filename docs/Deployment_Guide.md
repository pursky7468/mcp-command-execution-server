# MCP Command Execution Server - 部署指南

## 📋 概述

本指南提供 MCP Command Execution Server 的完整部署說明，涵蓋從系統需求到生產環境部署的所有步驟。

## 🎯 部署方式概覽

| 部署方式 | 適用場景 | 複雜度 | 推薦指數 |
|----------|----------|--------|----------|
| 本地直接安裝 | 開發測試、個人使用 | ⭐ | ⭐⭐⭐⭐⭐ |
| Docker 容器 | 隔離環境、快速部署 | ⭐⭐ | ⭐⭐⭐⭐ |
| Docker Compose | 多服務編排 | ⭐⭐⭐ | ⭐⭐⭐ |
| 雲端部署 | 生產環境、高可用性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 💻 系統需求

### 最低需求
```yaml
作業系統: Windows 10+ / Linux / macOS
Python: 3.8+
記憶體: 512MB RAM
硬碟: 100MB 可用空間
網路: 可連接 PyPI（用於安裝依賴）
權限: 讀寫工作目錄權限
```

### 建議需求
```yaml
作業系統: Windows 11 / Ubuntu 20.04+ / macOS 12+
Python: 3.9+
記憶體: 2GB+ RAM
硬碟: 1GB+ 可用空間（SSD 推薦）
網路: 穩定網路連線
權限: 適當的檔案系統權限
```

### 支援的 MCP 客戶端
- ✅ Claude Desktop
- ✅ VS Code with MCP Extension
- ✅ 其他 MCP 相容客戶端

---

## 🔧 方式一：本地直接安裝

### 步驟 1：環境準備

**檢查 Python 版本**：
```bash
python --version
# 應輸出 Python 3.8 或更高版本
```

**如果沒有 Python，請安裝**：
```bash
# Windows - 使用 Microsoft Store 或官網下載
# https://www.python.org/downloads/

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip

# Linux (CentOS/RHEL)
sudo yum install python3 python3-pip

# macOS - 使用 Homebrew
brew install python3
```

### 步驟 2：下載專案

**方法 A：使用 Git**：
```bash
git clone https://github.com/pursky7468/mcp-command-execution-server.git
cd mcp-command-execution-server
```

**方法 B：下載 ZIP**：
```bash
# 從 GitHub 下載 ZIP 檔案並解壓縮
wget https://github.com/pursky7468/mcp-command-execution-server/archive/main.zip
unzip main.zip
cd mcp-command-execution-server-main
```

### 步驟 3：安裝依賴

**建立虛擬環境（推薦）**：
```bash
# 建立虛擬環境
python -m venv mcp_env

# 啟動虛擬環境
# Windows
mcp_env\Scripts\activate
# Linux/macOS
source mcp_env/bin/activate
```

**安裝依賴套件**：
```bash
pip install -r requirements.txt
```

**驗證安裝**：
```bash
python server_fastmcp_fixed_v3_encoding.py --help
```

### 步驟 4：基本設定

**建立設定檔（可選）**：
```bash
# 複製設定範本
cp config.example.py config.py

# 編輯設定
nano config.py  # Linux/macOS
notepad config.py  # Windows
```

**環境變數設定**：
```bash
# Windows
set MCP_WORKING_DIR=C:\Your\Project\Path
set MCP_DEFAULT_TIMEOUT=60
set MCP_ENCODING=cp950

# Linux/macOS
export MCP_WORKING_DIR=/path/to/your/project
export MCP_DEFAULT_TIMEOUT=60
export MCP_ENCODING=utf-8
```

### 步驟 5：啟動服務

**直接啟動**：
```bash
python server_fastmcp_fixed_v3_encoding.py
```

**背景執行（Linux/macOS）**：
```bash
nohup python server_fastmcp_fixed_v3_encoding.py &
```

**Windows 服務方式**：
```bash
# 使用 NSSM (Non-Sucking Service Manager)
nssm install MCPServer "C:\path\to\python.exe" "C:\path\to\server_fastmcp_fixed_v3_encoding.py"
nssm start MCPServer
```

---

## 🐳 方式二：Docker 部署

### 步驟 1：安裝 Docker

**Windows**：
```bash
# 下載並安裝 Docker Desktop
# https://www.docker.com/products/docker-desktop/
```

**Linux (Ubuntu)**：
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

**macOS**：
```bash
# 下載並安裝 Docker Desktop
# 或使用 Homebrew
brew install --cask docker
```

### 步驟 2：建立 Dockerfile

**建立 Dockerfile**：
```dockerfile
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 複製需求檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式檔案
COPY server_fastmcp_fixed_v3_encoding.py .
COPY . .

# 建立工作目錄
RUN mkdir -p /app/workspace

# 設定環境變數
ENV MCP_WORKING_DIR=/app/workspace
ENV MCP_DEFAULT_TIMEOUT=60
ENV PYTHONUNBUFFERED=1

# 暴露埠號（如果需要）
EXPOSE 8000

# 啟動命令
CMD ["python", "server_fastmcp_fixed_v3_encoding.py"]
```

### 步驟 3：建立映像檔

```bash
# 建立 Docker 映像檔
docker build -t mcp-command-server .

# 檢查映像檔
docker images
```

### 步驟 4：執行容器

**基本執行**：
```bash
docker run -d \
  --name mcp-server \
  -v $(pwd)/workspace:/app/workspace \
  mcp-command-server
```

**進階執行（含埠號映射）**：
```bash
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  -v $(pwd)/workspace:/app/workspace \
  -e MCP_WORKING_DIR=/app/workspace \
  -e MCP_DEFAULT_TIMEOUT=120 \
  mcp-command-server
```

### 步驟 5：管理容器

```bash
# 檢查容器狀態
docker ps

# 檢視日誌
docker logs mcp-server

# 進入容器
docker exec -it mcp-server bash

# 停止容器
docker stop mcp-server

# 重啟容器
docker restart mcp-server

# 刪除容器
docker rm mcp-server
```

---

## 🏗️ 方式三：Docker Compose

### 步驟 1：建立 docker-compose.yml

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    container_name: mcp-command-server
    restart: unless-stopped
    volumes:
      - ./workspace:/app/workspace
      - ./logs:/app/logs
    environment:
      - MCP_WORKING_DIR=/app/workspace
      - MCP_DEFAULT_TIMEOUT=120
      - MCP_ENCODING=utf-8
      - PYTHONUNBUFFERED=1
    ports:
      - "8000:8000"
    networks:
      - mcp-network
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 可選：監控服務
  monitoring:
    image: prom/prometheus:latest
    container_name: mcp-monitoring
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - mcp-network
    depends_on:
      - mcp-server

networks:
  mcp-network:
    driver: bridge

volumes:
  workspace:
  logs:
```

### 步驟 2：相關設定檔

**建立監控設定**：
```bash
mkdir -p monitoring
```

**prometheus.yml**：
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mcp-server'
    static_configs:
      - targets: ['mcp-server:8000']
```

### 步驟 3：啟動服務

```bash
# 啟動所有服務
docker-compose up -d

# 檢查服務狀態
docker-compose ps

# 檢視日誌
docker-compose logs -f mcp-server

# 停止所有服務
docker-compose down

# 重建並啟動
docker-compose up --build -d
```

---

## ☁️ 方式四：雲端部署

### AWS 部署

**使用 AWS ECS**：
```bash
# 1. 建立 ECR 倉庫
aws ecr create-repository --repository-name mcp-command-server

# 2. 取得登入權杖
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com

# 3. 標記映像檔
docker tag mcp-command-server:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/mcp-command-server:latest

# 4. 推送映像檔
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/mcp-command-server:latest
```

**ECS 任務定義範例**：
```json
{
  "family": "mcp-command-server",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "mcp-server",
      "image": "123456789012.dkr.ecr.us-west-2.amazonaws.com/mcp-command-server:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MCP_WORKING_DIR",
          "value": "/app/workspace"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mcp-command-server",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud 部署

**使用 Cloud Run**：
```bash
# 1. 建立專案
gcloud config set project YOUR_PROJECT_ID

# 2. 啟用 API
gcloud services enable run.googleapis.com

# 3. 建立映像檔
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/mcp-command-server

# 4. 部署服務
gcloud run deploy mcp-command-server \
  --image gcr.io/YOUR_PROJECT_ID/mcp-command-server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure 部署

**使用 Container Instances**：
```bash
# 1. 登入 Azure
az login

# 2. 建立資源群組
az group create --name mcp-rg --location eastus

# 3. 建立容器執行個體
az container create \
  --resource-group mcp-rg \
  --name mcp-command-server \
  --image YOUR_REGISTRY/mcp-command-server:latest \
  --dns-name-label mcp-server \
  --ports 8000
```

---

## 🔗 MCP 客戶端設定

### Claude Desktop 設定

**找到設定檔位置**：
```bash
# Windows
%APPDATA%\Claude\claude_desktop_config.json

# macOS
~/Library/Application Support/Claude/claude_desktop_config.json

# Linux
~/.config/Claude/claude_desktop_config.json
```

**設定檔內容**：
```json
{
  "mcpServers": {
    "command-execution": {
      "command": "python",
      "args": ["C:/path/to/server_fastmcp_fixed_v3_encoding.py"],
      "env": {
        "MCP_WORKING_DIR": "C:/path/to/your/project",
        "MCP_DEFAULT_TIMEOUT": "60"
      }
    }
  }
}
```

**Docker 版本設定**：
```json
{
  "mcpServers": {
    "command-execution": {
      "command": "docker",
      "args": [
        "exec", 
        "mcp-server", 
        "python", 
        "server_fastmcp_fixed_v3_encoding.py"
      ]
    }
  }
}
```

### VS Code 設定

**安裝 MCP 擴展**：
1. 開啟 VS Code
2. 前往擴展市集
3. 搜尋 "MCP" 並安裝相關擴展

**設定 settings.json**：
```json
{
  "mcp.servers": [
    {
      "name": "command-execution",
      "command": "python",
      "args": ["C:/path/to/server_fastmcp_fixed_v3_encoding.py"],
      "env": {
        "MCP_WORKING_DIR": "C:/path/to/your/project"
      }
    }
  ]
}
```

---

## ✅ 部署驗證

### 基本功能測試

**測試 1：檢查服務狀態**：
```bash
# 本地部署
python -c "
import subprocess
result = subprocess.run(['python', 'server_fastmcp_fixed_v3_encoding.py', '--test'], capture_output=True, text=True)
print('Status:', 'OK' if result.returncode == 0 else 'FAIL')
"

# Docker 部署
docker exec mcp-server python -c "print('Server is running')"
```

**測試 2：執行簡單命令**：
```python
# 透過 MCP 客戶端執行
result = execute_command("python --version")
print(f"Python version: {result['data']['stdout']}")
```

**測試 3：檢查編碼處理**：
```python
# 測試中文編碼
result = execute_command("echo 測試中文")
print(f"Encoding used: {result['data']['encoding_used']}")
```

### 效能測試

**測試同時執行多個命令**：
```python
import concurrent.futures
import time

def test_command():
    return execute_command("python --version")

start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(test_command) for _ in range(10)]
    results = [future.result() for future in futures]

end_time = time.time()
print(f"10 commands completed in {end_time - start_time:.2f} seconds")
```

### 安全性檢查

**檢查命令白名單**：
```python
# 測試被拒絕的命令
result = execute_command("rm -rf /")  # 應該被拒絕
assert result["status"] == "error"
print("Security check passed: dangerous command rejected")
```

**檢查工作目錄限制**：
```python
# 測試目錄權限
result = list_directory_safe("/etc")  # 可能被拒絕或限制
print(f"Directory access result: {result['status']}")
```

---

## 🔧 故障排除快速指南

### 常見問題

**問題 1：Python 版本不相容**
```bash
# 解決方案：升級 Python
python --version
pip install --upgrade pip
```

**問題 2：依賴安裝失敗**
```bash
# 解決方案：使用國內映像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

**問題 3：權限問題**
```bash
# Windows：以管理員身分執行
# Linux：檢查檔案權限
sudo chmod +x server_fastmcp_fixed_v3_encoding.py
```

**問題 4：編碼問題**
```bash
# 設定正確的環境變數
export PYTHONIOENCODING=utf-8  # Linux/macOS
set PYTHONIOENCODING=cp950     # Windows
```

### 日誌檢查

**啟用詳細日誌**：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**檢查 Docker 日誌**：
```bash
docker logs mcp-server --tail 100 -f
```

---

## 📊 效能調優建議

### 系統層面
- 使用 SSD 硬碟提升 I/O 效能
- 確保足夠的 RAM（建議 2GB+）
- 定期清理臨時檔案

### 應用層面
- 調整 `MCP_DEFAULT_TIMEOUT` 根據需求
- 使用虛擬環境避免依賴衝突
- 定期更新依賴套件

### 監控建議
- 設定日誌輪轉
- 監控記憶體使用量
- 追踪命令執行時間

---

**文檔版本**：v1.0  
**最後更新**：2025-06-12  
**適用版本**：MCP Command Execution Server v3+