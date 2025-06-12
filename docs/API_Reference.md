# MCP Command Execution Server - API 參考文檔

## 📋 概述

本文檔提供 MCP Command Execution Server 所有可用工具的完整 API 參考，包含詳細的參數說明、回傳值格式和實用範例。

## 🔧 統一 API 規範

### 回傳值格式標準

所有工具函數都遵循統一的回傳格式：

```python
{
    "status": "success" | "error",          # 執行狀態
    "data": {...},                          # 具體資料內容（僅 success 時包含）
    "message": "使用者友善的狀態訊息",        # 人類可讀的結果描述
    "details": "詳細錯誤資訊"                # 額外詳細資訊（可選）
}
```

### 錯誤處理規範

所有錯誤都會回傳結構化的錯誤資訊，包含：
- 明確的錯誤類型指示（emoji 前綴）
- 可執行的解決建議
- 安全的錯誤資訊（不洩露系統細節）

---

## 🛠️ 系統命令工具

### execute_command

**功能描述**：執行系統命令的核心工具，支援智能編碼處理和安全驗證。

**函數簽名**：
```python
def execute_command(
    command: str, 
    working_directory: str = WORKING_DIRECTORY, 
    timeout: int = 30
) -> Dict[str, Any]
```

#### 參數詳細說明

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `command` | str | ✅ | - | 要執行的命令字串 |
| `working_directory` | str | ❌ | `C:\Users\User\Desktop\LineBot` | 命令執行的工作目錄 |
| `timeout` | int | ❌ | 30 | 命令執行超時時間（秒） |

#### 成功回傳格式
```python
{
    "status": "success",
    "data": {
        "command": "python --version",                    # 執行的完整命令
        "working_directory": "C:\\Users\\User\\Desktop\\LineBot",  # 實際工作目錄
        "exit_code": 0,                                   # 程序退出碼
        "stdout": "Python 3.9.7",                        # 標準輸出（已解碼）
        "stderr": "",                                     # 標準錯誤輸出（已解碼）
        "success": true,                                  # exit_code == 0
        "encoding_used": {                                # 使用的字符編碼
            "stdout": "cp950",
            "stderr": "cp950"
        }
    },
    "message": "✅ 命令執行完成"
}
```

#### 錯誤情況

**命令不在白名單**：
```python
{
    "status": "error",
    "message": "❌ 命令 'forbidden_cmd' 不被允許",
    "allowed_commands": ["python", "pip", "git", ...]
}
```

**執行超時**：
```python
{
    "status": "error",
    "message": "⏰ 命令執行超時（30秒）",
    "details": "建議：檢查命令是否需要用戶輸入或產生過多輸出"
}
```

#### 使用範例

**基本命令執行**：
```python
# 檢查 Python 版本
result = execute_command("python --version")
if result["status"] == "success":
    print(f"Python 版本：{result['data']['stdout']}")
```

**指定工作目錄**：
```python
# 在特定目錄執行命令
result = execute_command(
    "dir *.py", 
    working_directory="C:\\MyProject",
    timeout=10
)
```

**處理有錯誤的命令**：
```python
result = execute_command("python non_existent_script.py")
if result["data"]["exit_code"] != 0:
    print(f"執行失敗：{result['data']['stderr']}")
```

#### 支援的命令白名單
```python
ALLOWED_COMMANDS = [
    "python",    # Python 解釋器
    "pip",       # Python 套件管理器
    "git",       # Git 版本控制
    "dir",       # Windows 目錄列表
    "ls",        # Unix 目錄列表
    "cd",        # 切換目錄
    "mkdir",     # 建立目錄
    "copy",      # 複製檔案 (Windows)
    "move",      # 移動檔案 (Windows)  
    "del",       # 刪除檔案 (Windows)
    "type",      # 顯示檔案內容 (Windows)
    "cat",       # 顯示檔案內容 (Unix)
    "cls",       # 清除螢幕 (Windows)
    "clear",     # 清除螢幕 (Unix)
    "chcp"       # 變更代碼頁 (Windows)
]
```

---

### list_directory_safe

**功能描述**：安全的目錄瀏覽工具，使用 Python 原生功能避免命令執行和編碼問題。

**函數簽名**：
```python
def list_directory_safe(path: str = None) -> Dict[str, Any]
```

#### 參數說明

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `path` | str | ❌ | 當前工作目錄 | 要列出的目錄路徑 |

#### 成功回傳格式
```python
{
    "status": "success",
    "data": {
        "path": "C:\\Users\\User\\Desktop\\LineBot",       # 絕對路徑
        "total_items": 15,                                 # 總項目數
        "directories": 3,                                  # 目錄數量
        "files": 12,                                       # 檔案數量
        "total_size": 1048576,                            # 總大小（bytes）
        "total_size_readable": "1.0 MB",                  # 人類可讀的大小
        "contents": [
            {
                "name": "main.py",                         # 項目名稱
                "type": "📄",                              # 類型圖示（📁目錄/📄檔案）
                "is_directory": false,                     # 是否為目錄
                "path": "C:\\...\\main.py",               # 完整路徑
                "size": 2048,                             # 檔案大小（bytes）
                "size_readable": "2.0 KB"                # 人類可讀的大小
            },
            {
                "name": "src",
                "type": "📁",
                "is_directory": true,
                "path": "C:\\...\\src",
                "items": 5                                # 目錄中的項目數
            }
        ]
    },
    "message": "✅ 成功取得目錄資訊：15 個項目（📁3 目錄，📄12 檔案）"
}
```

#### 錯誤情況

**目錄不存在**：
```python
{
    "status": "error",
    "message": "❌ 目錄不存在：C:\\NonExistent"
}
```

**權限不足**：
```python
{
    "status": "error", 
    "message": "❌ 取得目錄資訊時發生錯誤：Permission denied"
}
```

#### 使用範例

**列出當前目錄**：
```python
result = list_directory_safe()
if result["status"] == "success":
    data = result["data"]
    print(f"目錄：{data['path']}")
    print(f"包含 {data['directories']} 個目錄和 {data['files']} 個檔案")
    
    for item in data["contents"]:
        print(f"{item['type']} {item['name']}")
```

**列出特定目錄**：
```python
result = list_directory_safe("C:\\Users\\User\\Documents")
```

**篩選特定類型檔案**：
```python
result = list_directory_safe()
if result["status"] == "success":
    python_files = [
        item for item in result["data"]["contents"] 
        if item["name"].endswith(".py")
    ]
    print(f"找到 {len(python_files)} 個 Python 檔案")
```

---

## 🐍 Python 專用工具

### run_python_script

**功能描述**：專門執行 Python 腳本的工具，提供更好的 Python 環境整合。

**函數簽名**：
```python
def run_python_script(
    script_name: str, 
    args: List[str] = None, 
    timeout: int = 60
) -> Dict[str, Any]
```

#### 參數說明

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `script_name` | str | ✅ | - | Python 腳本檔名（相對於工作目錄） |
| `args` | List[str] | ❌ | [] | 傳遞給腳本的命令列參數 |
| `timeout` | int | ❌ | 60 | 腳本執行超時時間（秒） |

#### 回傳格式
回傳格式與 `execute_command` 相同，但命令會自動添加 `python` 前綴。

#### 使用範例

**執行簡單腳本**：
```python
result = run_python_script("test.py")
```

**傳遞命令列參數**：
```python
result = run_python_script("data_processor.py", [
    "--input", "data.csv",
    "--output", "results.json",
    "--verbose"
])
```

**長時間運行的腳本**：
```python
result = run_python_script("train_model.py", timeout=3600)  # 1小時超時
```

**錯誤處理**：
```python
result = run_python_script("script_with_error.py")
if result["status"] == "success" and not result["data"]["success"]:
    print("腳本執行完成但有錯誤：")
    print(result["data"]["stderr"])
```

---

### check_python_environment

**功能描述**：檢查 Python 環境和相關配置資訊。

**函數簽名**：
```python
def check_python_environment() -> Dict[str, Any]
```

#### 參數說明
此函數無需參數。

#### 成功回傳格式
```python
{
    "status": "success",
    "data": {
        "python_version": {                               # Python 版本資訊
            "stdout": "Python 3.9.7",
            "exit_code": 0
        },
        "pip_version": {                                  # pip 版本資訊
            "stdout": "pip 21.3.1 from C:\\...",
            "exit_code": 0
        },
        "has_requirements_txt": true,                     # 是否有 requirements.txt
        "working_directory": "C:\\Users\\User\\Desktop\\LineBot",  # 工作目錄
        "console_encoding": "cp950",                      # 控制台編碼
        "system_locale": "cp950",                        # 系統 locale
        "installed_packages_count": 25,                  # 已安裝套件數量
        "sample_packages": [                             # 前10個套件範例
            "fastmcp==0.1.0",
            "chardet==4.0.0",
            "requests==2.28.1"
        ]
    },
    "message": "✅ Python 環境檢查完成"
}
```

#### 使用範例

**基本環境檢查**：
```python
result = check_python_environment()
if result["status"] == "success":
    data = result["data"]
    print(f"Python 版本：{data['python_version']['stdout']}")
    print(f"已安裝 {data['installed_packages_count']} 個套件")
```

**檢查特定套件是否安裝**：
```python
result = check_python_environment()
if result["status"] == "success":
    packages = result["data"]["sample_packages"]
    has_requests = any("requests" in pkg for pkg in packages)
    print(f"requests 已安裝：{has_requests}")
```

---

### install_requirements

**功能描述**：安裝 requirements.txt 中列出的依賴套件。

**函數簽名**：
```python
def install_requirements() -> Dict[str, Any]
```

#### 參數說明
此函數無需參數，會自動尋找工作目錄中的 `requirements.txt` 檔案。

#### 成功回傳格式
```python
{
    "status": "success",
    "data": {
        "command": "pip install -r requirements.txt",
        "working_directory": "C:\\Users\\User\\Desktop\\LineBot",
        "exit_code": 0,
        "stdout": "Successfully installed fastmcp-0.1.0 chardet-4.0.0",
        "stderr": "",
        "success": true,
        "encoding_used": {"stdout": "cp950", "stderr": "cp950"}
    },
    "message": "✅ 命令執行完成"
}
```

#### 錯誤情況

**requirements.txt 不存在**：
```python
{
    "status": "error",
    "message": "❌ 找不到 requirements.txt 檔案：C:\\...\\requirements.txt"
}
```

#### 使用範例

**基本套件安裝**：
```python
result = install_requirements()
if result["status"] == "success" and result["data"]["success"]:
    print("套件安裝成功")
else:
    print("安裝失敗，錯誤資訊：")
    print(result["data"]["stderr"])
```

---

## 📁 Git 整合工具

### get_git_status

**功能描述**：取得 Git 倉庫的狀態資訊，包含分支、檔案變更等。

**函數簽名**：
```python
def get_git_status() -> Dict[str, Any]
```

#### 參數說明
此函數無需參數，會檢查當前工作目錄的 Git 狀態。

#### 成功回傳格式
```python
{
    "status": "success",
    "data": {
        "current_branch": "main",                         # 當前分支
        "modified_files": [                              # 已修改的檔案
            "src/main.py",
            "config.json"
        ],
        "added_files": [                                 # 已添加到暫存區的檔案
            "new_feature.py"
        ],
        "deleted_files": [                               # 已刪除的檔案
            "old_script.py"
        ],
        "untracked_files": [                             # 未追蹤的檔案
            "temp.log",
            ".env"
        ],
        "total_changes": 5,                              # 總變更數
        "is_clean": false                                # 工作區是否乾淨
    },
    "message": "✅ Git 狀態檢查完成"
}
```

#### 錯誤情況

**不是 Git 倉庫**：
```python
{
    "status": "error",
    "message": "❌ 此目錄不是 Git 倉庫或 Git 未正確設定"
}
```

#### 使用範例

**檢查基本狀態**：
```python
result = get_git_status()
if result["status"] == "success":
    data = result["data"]
    print(f"當前分支：{data['current_branch']}")
    
    if data["is_clean"]:
        print("工作區乾淨，沒有未提交的變更")
    else:
        print(f"有 {data['total_changes']} 個變更待處理")
```

**列出變更檔案**：
```python
result = get_git_status()
if result["status"] == "success":
    data = result["data"]
    
    if data["modified_files"]:
        print("已修改的檔案：")
        for file in data["modified_files"]:
            print(f"  📝 {file}")
    
    if data["untracked_files"]:
        print("未追蹤的檔案：")
        for file in data["untracked_files"]:
            print(f"  ❓ {file}")
```

---

## 🌡️ 領域特定工具

以下是一些專門為特定應用場景設計的工具。

### create_temperature

**功能描述**：建立溫度值物件，支援攝氏和華氏度。

**函數簽名**：
```python
def create_temperature(value: float, unit: str = "CELSIUS") -> Dict[str, Any]
```

#### 參數說明

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `value` | float | ✅ | - | 溫度數值 |
| `unit` | str | ❌ | "CELSIUS" | 溫度單位（"CELSIUS" 或 "FAHRENHEIT"） |

#### 使用範例
```python
# 建立攝氏溫度
temp_c = create_temperature(25.5, "CELSIUS")

# 建立華氏溫度  
temp_f = create_temperature(77.9, "FAHRENHEIT")
```

### convert_temperature

**功能描述**：轉換溫度單位。

**函數簽名**：
```python
def convert_temperature(
    value: float, 
    from_unit: str, 
    to_unit: str
) -> Dict[str, Any]
```

#### 使用範例
```python
# 攝氏轉華氏
result = convert_temperature(25, "CELSIUS", "FAHRENHEIT")
# 華氏轉攝氏
result = convert_temperature(77, "FAHRENHEIT", "CELSIUS")
```

### calculate_wind_chill

**功能描述**：計算體感溫度（風寒指數）。

**函數簽名**：
```python
def calculate_wind_chill(temperature: float, wind_speed: float) -> Dict[str, Any]
```

#### 參數說明

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `temperature` | float | ✅ | 實際氣溫（攝氏度） |
| `wind_speed` | float | ✅ | 風速（km/h） |

---

## 👔 服裝建議工具

### get_clothing_type_info
取得特定服裝類型的詳細資訊。

### list_clothing_types_by_category  
列出特定類別的所有服裝類型。

### check_clothing_compatibility
檢查兩種服裝類型的相容性。

---

## 🌦️ 天氣相關工具

### get_weather_condition_info
取得天氣狀況的詳細資訊。

### compare_weather_conditions
比較多個天氣狀況的優先級。

### create_weather_tag
建立自定義天氣標籤。

### check_tag_weather_compatibility
檢查天氣標籤與天氣狀況的相容性。

---

## 🔍 工具使用最佳實踐

### 1. 錯誤處理
```python
result = any_tool_function(params)

# 標準錯誤檢查
if result["status"] == "error":
    print(f"操作失敗：{result['message']}")
    return

# 命令執行類工具的額外檢查
if "data" in result and "success" in result["data"]:
    if not result["data"]["success"]:
        print(f"命令執行失敗：{result['data']['stderr']}")
```

### 2. 超時處理
```python
# 對於可能長時間運行的操作，設定適當的超時
result = execute_command("long_running_command", timeout=300)  # 5分鐘

result = run_python_script("train_model.py", timeout=3600)     # 1小時
```

### 3. 路徑處理
```python
# 使用絕對路徑避免路徑問題
import os
abs_path = os.path.abspath("relative/path")
result = execute_command("command", working_directory=abs_path)
```

### 4. 編碼處理
```python
# 檢查使用的編碼
result = execute_command("echo 中文測試")
if result["status"] == "success":
    encoding_info = result["data"]["encoding_used"]
    print(f"標準輸出使用編碼：{encoding_info['stdout']}")
```

---

**文檔版本**：v1.0  
**最後更新**：2025-06-12  
**涵蓋工具數量**：15+ 個工具函數