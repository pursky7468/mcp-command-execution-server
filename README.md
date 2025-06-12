# MCP Command Execution Server

這個 MCP Server 提供命令執行工具，讓 Claude 可以直接執行系統命令。

## 🚀 安裝步驟

### 1. 安裝依賴
```bash
cd C:\Users\User\Desktop\mcp_command_server
pip install -r requirements.txt
```

### 2. 測試 MCP Server
```bash
python server.py
```

### 3. 配置 Claude Desktop

將以下配置添加到您的 Claude Desktop 配置檔案中：

**Windows 配置檔案位置：**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**配置內容：**
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

## 🛠️ 可用工具

### 1. execute_command
執行系統命令
```
執行: cd C:\Users\User\Desktop\LineBot && python test_architecture.py
```

### 2. run_python_script  
在 LineBot 目錄中執行 Python 腳本
```
執行: test_architecture.py
```

### 3. change_directory
更改工作目錄
```
更改到: C:\Users\User\Desktop\LineBot
```

### 4. get_directory_info
取得目錄資訊
```
查看: C:\Users\User\Desktop\LineBot
```

## 🔒 安全特性

- 只允許執行白名單中的命令
- 預設工作目錄限制在 LineBot 專案
- 命令執行有超時限制
- 完整的錯誤處理和日誌

## 📝 使用範例

安裝完成後，您可以要求 Claude：

1. **測試架構**：
   "請執行 test_architecture.py 來測試新架構"

2. **查看目錄**：
   "請檢查 LineBot 目錄的內容"

3. **執行 Git 命令**：
   "請檢查 Git 狀態"

4. **安裝依賴**：
   "請安裝 requirements.txt 中的依賴"

## 🚨 重要注意事項

1. **重啟 Claude Desktop**：修改配置後需要重啟 Claude Desktop
2. **路徑正確性**：確保所有路徑都正確設定
3. **Python 環境**：確保使用正確的 Python 環境
4. **權限**：確保有執行相關命令的權限
