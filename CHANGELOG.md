# Changelog

此文件記錄了 MCP Command Execution Server 的所有重要變更。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
版本編號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [Unreleased] - 開發中

### 🔄 計劃中
- 添加命令執行權限管理
- 實作命令執行歷史記錄
- 支援批次命令執行
- 添加命令執行效能監控
- 實作安全沙箱執行環境
- 支援自定義命令別名

### 🏗️ 架構改進計劃
- 實作命令執行佇列系統
- 添加分散式命令執行支援
- 實作實時執行狀態回報
- 添加命令執行結果快取

---

## [1.3.0] - 2024-12-XX (目前版本) ✨ 編碼問題完全解決

### 🚀 新增功能
- **智能編碼偵測**: 自動偵測並處理多種中文編碼
- **Windows 特殊處理**: 針對 Windows 控制台編碼優化
- **編碼回報機制**: 顯示實際使用的編碼格式
- **多層編碼嘗試**: 按優先順序嘗試多種編碼方案

### 🔧 重大修正
- **完全解決中文亂碼問題**: 支援 CP950、Big5、GBK、UTF-8
- **修正 subprocess 卡住問題**: 添加 `stdin=subprocess.DEVNULL`
- **Git 命令特殊處理**: 強制無互動模式執行
- **記憶體洩漏修正**: 優化長時間運行穩定性

### 📈 效能改進
- **智能編碼偵測**: 使用 chardet 庫提高偵測準確性
- **編碼優先順序**: 針對繁體中文環境優化編碼順序
- **錯誤處理增強**: 更詳細的錯誤訊息和除錯資訊
- **執行效率提升**: 減少不必要的編碼轉換

### 🛠️ 技術改進
- **Bytes 模式執行**: 避免 Python 自動編碼轉換
- **環境變數控制**: 強制設定 Python IO 編碼
- **Windows 創建旗標**: 避免顯示額外的控制台視窗
- **超時機制優化**: 更可靠的命令執行超時處理

---

## [1.2.0] - 2024-12-XX

### 🚀 新增功能
- **Python 環境檢查工具**: `check_python_environment()`
- **Git 狀態查詢功能**: `get_git_status()`
- **需求套件安裝**: `install_requirements()`
- **安全目錄列表**: `list_directory_safe()`

### 🔧 修正
- 修正長時間執行命令的超時問題
- 改善錯誤訊息的可讀性
- 優化記憶體使用效率

### 📈 改進
- 提升命令執行穩定性
- 改善日誌記錄格式
- 優化工具函數效能

---

## [1.1.0] - 2024-12-XX

### 🚀 新增功能
- **FastMCP 框架整合**: 使用 FastMCP 簡化 MCP 工具開發
- **模組化工具設計**: 每個功能獨立為 MCP 工具
- **增強錯誤處理**: 統一的錯誤處理和回應格式
- **命令白名單機制**: 提升安全性的命令限制

### 🔄 重構項目
- `server.py` → 基礎版本保留
- `server_fastmcp.py` → FastMCP 框架版本
- 所有工具函數模組化
- 統一回應格式標準化

### 🛡️ 安全性提升
- 實作命令白名單檢查
- 工作目錄限制機制
- 執行超時保護
- 完整的錯誤追蹤

---

## [1.0.0] - 2024-12-XX 🎉 首次發布

### 🚀 核心功能
- **MCP Server 整合**: 完整的 Model Context Protocol 支援
- **命令執行引擎**: 安全的系統命令執行功能
- **Claude Desktop 整合**: 無縫整合 Claude Desktop
- **工作目錄管理**: 彈性的工作目錄控制

### 🏗️ 技術基礎
- Python MCP SDK 整合
- subprocess 命令執行
- JSON 格式配置支援
- 基礎安全機制

### 📱 核心工具
- `execute_command`: 執行系統命令
- `run_python_script`: 執行 Python 腳本
- `change_directory`: 更改工作目錄
- `get_directory_info`: 取得目錄資訊

### 🛡️ 安全特性
- 命令白名單限制
- 工作目錄限制
- 執行超時保護
- 錯誤處理機制

---

## 版本說明

### 版本編號規則
- **主版本號 (Major)**: 不相容的 API 變更
- **次版本號 (Minor)**: 向下相容的新功能  
- **修訂版本號 (Patch)**: 向下相容的問題修正

### 變更類型說明
- 🚀 **新增 (Added)**: 新功能
- 🔄 **變更 (Changed)**: 現有功能的變更
- 🗑️ **棄用 (Deprecated)**: 即將移除的功能
- ❌ **移除 (Removed)**: 已移除的功能
- 🔧 **修正 (Fixed)**: 錯誤修正
- 🛡️ **安全 (Security)**: 安全性相關變更
- 📈 **改進 (Improved)**: 效能或可用性改進
- 🏗️ **重構 (Refactor)**: 架構層面的變更

---

## 維護政策

### 支援版本
- **目前版本 (1.3.x)**: 完整支援，持續開發
- **前一版本 (1.2.x)**: 安全性修正，錯誤修正
- **更早版本**: 不再支援

### 升級建議
- 強烈建議升級至最新的 1.3.x 版本
- 編碼問題修正帶來更穩定的中文支援
- 提供更可靠的命令執行體驗

---

## 技術規格

### 系統需求
- Python 3.8+
- Windows 10/11 (主要測試環境)
- Claude Desktop (MCP 整合)

### 相依套件
- `fastmcp`: MCP 框架支援
- `chardet`: 編碼自動偵測
- 標準庫: `subprocess`, `pathlib`, `locale`

### 支援編碼
- CP950 (Windows 繁體中文)
- Big5 (繁體中文)
- CP936/GBK (簡體中文)
- UTF-8 (國際標準)
- UTF-16 (Windows Unicode)

---

## 參與貢獻

歡迎參與專案開發！請查看開發指南了解詳細資訊。

### 報告問題
請提供以下資訊：
- 作業系統版本
- Python 版本
- 命令執行內容
- 錯誤訊息和編碼資訊

### 功能建議
歡迎建議新的 MCP 工具功能或安全性改進。

---

## 致謝

感謝以下專案和社群的支援：
- [FastMCP](https://github.com/jlowin/fastmcp) - 簡化 MCP 開發的優秀框架
- [Model Context Protocol](https://github.com/modelcontextprotocol) - 標準化的上下文協議
- [Claude Desktop](https://claude.ai) - 提供優秀的 MCP 整合平台
