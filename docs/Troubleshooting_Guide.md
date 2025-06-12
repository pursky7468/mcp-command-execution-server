# MCP Command Server 故障排除指南

## 📚 目錄

- [常見問題與解決方案](#常見問題與解決方案)
- [日誌與除錯方法](#日誌與除錯方法)
- [效能診斷](#效能診斷)
- [環境問題排除](#環境問題排除)
- [安全問題排除](#安全問題排除)

## 常見問題與解決方案

### 🔧 MCP 服務器無法啟動

#### 問題症狀
- Claude Desktop 無法連接到 MCP 服務器
- 配置檔案無反應
- 連接超時

#### 可能原因與解決方案

**1. Python 環境問題**
```bash
# 檢查 Python 版本
python --version
# 應該返回 Python 3.8 或更新版本

# 檢查 FastMCP 是否正確安裝
pip show fastmcp

# 重新安裝依賴
pip install -r requirements.txt
```

**2. 路徑配置錯誤**
```json
{
  "mcpServers": {
    "command-execution": {
      "command": "python",
      "args": ["C:\\Users\\User\\Desktop\\mcp_command_server\\server.py"],
      "env": {
        "PYTHONPATH": "C:\\Users\\User\\Desktop\\mcp_command_server"
      }
    }
  }
}
```

**檢查清單：**
- ✅ 確認 Python 路徑正確
- ✅ 確認 server.py 檔案存在
- ✅ 確認路徑使用雙反斜線（Windows）

**3. 權限問題**
```powershell
# 以管理員身份執行 PowerShell
# 檢查目錄權限
icacls "C:\Users\User\Desktop\mcp_command_server"

# 給予完整權限（如需要）
icacls "C:\Users\User\Desktop\mcp_command_server" /grant Users:F
```

### 🔧 命令執行失敗

#### 問題症狀
- 命令返回錯誤代碼
- 輸出亂碼或為空
- 執行超時

#### 解決方案

**1. 編碼問題**
```python
# 檢查系統編碼
import locale
print(f"系統編碼: {locale.getpreferredencoding()}")

# 強制設定編碼環境變數
set PYTHONIOENCODING=cp950
```

**2. 路徑問題**
```python
# 檢查工作目錄
import os
print(f"當前目錄: {os.getcwd()}")

# 檢查檔案是否存在
import pathlib
path = pathlib.Path("your_script.py")
print(f"檔案存在: {path.exists()}")
```

**3. 超時問題**
```python
# 增加超時時間
execute_command("long_running_command", timeout=300)

# 或使用非同步執行
run_python_script("script.py", timeout=600)
```

### 🔧 Git 操作問題

#### 問題症狀
- Git 狀態檢查失敗
- 中文檔名顯示異常
- Git 命令卡住

#### 解決方案

**1. Git 配置問題**
```bash
# 檢查 Git 版本
git --version

# 設定中文檔名支援
git config --global core.quotepath false

# 設定編碼
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
```

**2. 權限問題**
```bash
# 檢查 Git 倉庫狀態
git status

# 重新初始化（如需要）
git init

# 檢查遠端設定
git remote -v
```

### 🔧 Python 腳本執行問題

#### 問題症狀
- 腳本找不到模組
- Import 錯誤
- 相對路徑問題

#### 解決方案

**1. 模組路徑問題**
```python
# 在腳本開頭添加
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

**2. 依賴安裝問題**
```bash
# 檢查已安裝套件
pip list

# 安裝特定版本
pip install package_name==version

# 升級套件
pip install --upgrade package_name
```

## 日誌與除錯方法

### 📊 啟用詳細日誌

#### 修改 server.py 啟用除錯模式

```python
import logging

# 設定日誌等級
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

#### 在工具函數中添加日誌

```python
@mcp.tool()
def execute_command(command: str, working_directory: str = WORKING_DIRECTORY, timeout: int = 30):
    logger.info(f"執行命令: {command}")
    logger.debug(f"工作目錄: {working_directory}")
    logger.debug(f"超時設定: {timeout}秒")
    
    try:
        result = execute_command_with_smart_encoding(command, working_directory, timeout)
        logger.info(f"命令執行完成，返回碼: {result.get('data', {}).get('exit_code', 'N/A')}")
        return result
    except Exception as e:
        logger.error(f"命令執行異常: {str(e)}")
        raise
```

### 📊 Claude Desktop 日誌檢查

#### Windows 日誌位置
```
%APPDATA%\Claude\logs\
```

#### 重要日誌檔案
- `main.log` - 主要應用程式日誌
- `mcp.log` - MCP 相關日誌
- `renderer.log` - 前端渲染日誌

#### 檢查 MCP 連接狀態
```bash
# 在 Claude Desktop 日誌中尋找
grep -i "mcp" %APPDATA%\Claude\logs\main.log
```

### 📊 系統層級除錯

#### 檢查程序狀態
```powershell
# 檢查 Python 程序
Get-Process python

# 檢查網路連接
netstat -an | findstr :3000
```

#### 檢查系統資源
```powershell
# 記憶體使用
Get-WmiObject -Class Win32_OperatingSystem | Select-Object TotalPhysicalMemory,FreePhysicalMemory

# CPU 使用率
Get-WmiObject -Class Win32_Processor | Select-Object LoadPercentage
```

## 效能診斷

### ⚡ 效能指標監控

#### 命令執行時間分析

```python
import time
import psutil
from functools import wraps

def performance_monitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 記錄開始時間和系統資源
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.Process().cpu_percent()
        
        try:
            result = func(*args, **kwargs)
            
            # 記錄結束時間和資源
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            end_cpu = psutil.Process().cpu_percent()
            
            # 計算效能指標
            execution_time = end_time - start_time
            memory_delta = end_memory - start_memory
            
            logger.info(f"效能指標 - 函數: {func.__name__}")
            logger.info(f"  執行時間: {execution_time:.3f}秒")
            logger.info(f"  記憶體變化: {memory_delta:.2f}MB")
            logger.info(f"  CPU 使用率: {end_cpu:.1f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"函數 {func.__name__} 執行失敗: {str(e)}")
            raise
            
    return wrapper

# 使用範例
@performance_monitor
def execute_command_with_monitoring(command, working_directory, timeout):
    return execute_command_with_smart_encoding(command, working_directory, timeout)
```

#### 系統資源監控

```python
def system_health_check():
    """系統健康狀態檢查"""
    try:
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 記憶體使用
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available = memory.available / 1024 / 1024  # MB
        
        # 磁碟使用
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        health_report = {
            "cpu_usage": cpu_percent,
            "memory_usage": memory_percent,
            "memory_available_mb": memory_available,
            "disk_usage": disk_percent,
            "status": "healthy" if cpu_percent < 80 and memory_percent < 85 else "warning"
        }
        
        logger.info(f"系統健康檢查: {health_report}")
        return health_report
        
    except Exception as e:
        logger.error(f"系統健康檢查失敗: {str(e)}")
        return {"status": "error", "message": str(e)}
```

### ⚡ 效能最佳化建議

#### 1. 命令執行最佳化

```python
# 避免重複的環境檢查
_env_cache = None

def get_optimized_env():
    global _env_cache
    if _env_cache is None:
        _env_cache = os.environ.copy()
        _env_cache.update({
            'PYTHONPATH': WORKING_DIRECTORY,
            'PYTHONUNBUFFERED': '1',
            'PYTHONIOENCODING': 'cp950'
        })
    return _env_cache

# 使用連接池減少重複初始化
class CommandExecutor:
    def __init__(self):
        self.env = get_optimized_env()
        self.working_directory = WORKING_DIRECTORY
    
    def execute(self, command, timeout=30):
        # 重用環境設定，減少初始化時間
        return subprocess.run(
            command,
            shell=True,
            cwd=self.working_directory,
            env=self.env,
            # ... 其他參數
        )
```

#### 2. 記憶體管理

```python
# 大量輸出的流式處理
def stream_command_output(command):
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
        bufsize=1
    )
    
    output_lines = []
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            decoded_line, _ = smart_decode_output(output)
            output_lines.append(decoded_line.strip())
            
            # 限制記憶體使用
            if len(output_lines) > 1000:
                output_lines = output_lines[-500:]  # 保留最後 500 行
    
    return output_lines
```

## 環境問題排除

### 🔍 Python 環境診斷

```python
def diagnose_python_environment():
    """Python 環境診斷工具"""
    report = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "python_path": sys.path,
        "working_directory": os.getcwd(),
        "environment_variables": {
            "PYTHONPATH": os.environ.get("PYTHONPATH"),
            "PYTHONIOENCODING": os.environ.get("PYTHONIOENCODING"),
            "PATH": os.environ.get("PATH")
        },
        "installed_packages": [],
        "encoding_info": {
            "preferred_encoding": locale.getpreferredencoding(),
            "default_encoding": sys.getdefaultencoding(),
            "filesystem_encoding": sys.getfilesystemencoding()
        }
    }
    
    # 檢查關鍵套件
    critical_packages = ["fastmcp", "subprocess", "pathlib"]
    for package in critical_packages:
        try:
            __import__(package)
            report["installed_packages"].append(f"{package}: ✅")
        except ImportError:
            report["installed_packages"].append(f"{package}: ❌")
    
    return report
```

### 🔍 網路連接診斷

```python
def diagnose_network():
    """網路連接診斷"""
    import socket
    
    def check_port(host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                return result == 0
        except:
            return False
    
    network_status = {
        "localhost_connection": check_port("127.0.0.1", 8080),
        "internet_connection": check_port("8.8.8.8", 53),
        "local_ports": []
    }
    
    return network_status
```

## 安全問題排除

### 🔒 權限檢查

```python
def check_security_permissions():
    """檢查安全權限設定"""
    security_report = {
        "working_directory_writable": os.access(WORKING_DIRECTORY, os.W_OK),
        "working_directory_readable": os.access(WORKING_DIRECTORY, os.R_OK),
        "python_executable_accessible": os.access(sys.executable, os.X_OK),
        "allowed_commands": ALLOWED_COMMANDS,
        "blocked_commands": []
    }
    
    # 檢查危險命令是否被正確阻擋
    dangerous_commands = ["rm", "del", "format", "shutdown", "reboot"]
    for cmd in dangerous_commands:
        if cmd not in ALLOWED_COMMANDS:
            security_report["blocked_commands"].append(f"{cmd}: ✅ 已阻擋")
        else:
            security_report["blocked_commands"].append(f"{cmd}: ⚠️ 允許執行")
    
    return security_report
```

### 🔒 安全建議

1. **最小權限原則**
   - 只授予必要的檔案系統權限
   - 定期檢查 ALLOWED_COMMANDS 清單
   - 避免以管理員權限執行

2. **網路安全**
   - 確保 MCP 服務器只監聽本地端口
   - 避免對外開放服務
   - 定期更新依賴套件

3. **日誌安全**
   - 避免在日誌中記錄敏感資訊
   - 定期清理舊日誌檔案
   - 保護日誌檔案存取權限

## 快速診斷腳本

建立一個快速診斷腳本：

```python
# diagnose.py
def run_full_diagnosis():
    """執行完整診斷"""
    print("🔍 MCP Command Server 診斷工具")
    print("=" * 50)
    
    # Python 環境
    print("\n📋 Python 環境檢查")
    python_report = diagnose_python_environment()
    for key, value in python_report.items():
        print(f"  {key}: {value}")
    
    # 網路連接
    print("\n🌐 網路連接檢查")
    network_report = diagnose_network()
    for key, value in network_report.items():
        print(f"  {key}: {'✅' if value else '❌'}")
    
    # 安全權限
    print("\n🔒 安全權限檢查")
    security_report = check_security_permissions()
    for key, value in security_report.items():
        print(f"  {key}: {value}")
    
    # 系統健康
    print("\n💊 系統健康檢查")
    health_report = system_health_check()
    for key, value in health_report.items():
        print(f"  {key}: {value}")
    
    print("\n✅ 診斷完成")

if __name__ == "__main__":
    run_full_diagnosis()
```

使用方式：
```bash
python diagnose.py
```

## 聯絡支援

如果問題仍然無法解決，請收集以下資訊：

1. **系統資訊**
   - 作業系統版本
   - Python 版本
   - 錯誤訊息完整內容

2. **日誌檔案**
   - MCP 服務器日誌
   - Claude Desktop 日誌
   - 系統事件日誌

3. **配置檔案**
   - claude_desktop_config.json
   - 環境變數設定

將這些資訊整理後，可以在 GitHub Issues 中回報問題。
