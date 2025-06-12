#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server for Command Execution Tools (使用 FastMCP)

基於您現有架構改善的命令執行工具
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

from fastmcp import FastMCP

# 建立 FastMCP 實例
mcp = FastMCP("command-execution-server")

# 全域配置
WORKING_DIRECTORY = r"C:\Users\User\Desktop\LineBot"
ALLOWED_COMMANDS = [
    "python", "pip", "git", "dir", "ls", "cd", "mkdir", 
    "copy", "move", "del", "type", "cat", "cls", "clear"
]

# ===== 命令執行工具 =====

@mcp.tool()
def execute_command(command: str, working_directory: str = WORKING_DIRECTORY, timeout: int = 30) -> Dict[str, Any]:
    """
    執行系統命令
    
    參數:
    command (str): 要執行的命令
    working_directory (str): 工作目錄（預設：LineBot 專案目錄）
    timeout (int): 超時時間（秒，預設：30）
    
    返回:
    Dict: 包含執行結果的字典
    """
    try:
        # 安全檢查 - 只允許白名單中的命令
        command_parts = command.split()
        if command_parts and command_parts[0] not in ALLOWED_COMMANDS:
            return {
                "status": "error",
                "message": f"❌ 命令 '{command_parts[0]}' 不被允許",
                "allowed_commands": ALLOWED_COMMANDS
            }
        
        # 確保工作目錄存在
        Path(working_directory).mkdir(parents=True, exist_ok=True)
        
        # 執行命令
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        
        return {
            "status": "success",
            "data": {
                "command": command,
                "working_directory": working_directory,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            },
            "message": "✅ 命令執行完成" if result.returncode == 0 else "⚠️ 命令執行完成但有錯誤"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": f"⏰ 命令執行超時（{timeout}秒）"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ 執行命令時發生錯誤：{str(e)}"
        }


@mcp.tool()
def run_python_script(script_name: str, args: List[str] = None, timeout: int = 60) -> Dict[str, Any]:
    """
    在 LineBot 專案目錄中執行 Python 腳本
    
    參數:
    script_name (str): Python 腳本名稱（如 'test_architecture.py'）
    args (List[str]): 命令列參數（可選）
    timeout (int): 超時時間（秒，預設：60）
    
    返回:
    Dict: 包含執行結果的字典
    """
    try:
        if args is None:
            args = []
        
        # 建構完整命令
        command_parts = ["python", script_name] + args
        command = " ".join(command_parts)
        
        # 使用 execute_command 函數
        return execute_command(command, WORKING_DIRECTORY, timeout)
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ 執行 Python 腳本時發生錯誤：{str(e)}"
        }


@mcp.tool()
def change_working_directory(path: str) -> Dict[str, Any]:
    """
    更改預設工作目錄
    
    參數:
    path (str): 新的工作目錄路徑
    
    返回:
    Dict: 包含操作結果的字典
    """
    global WORKING_DIRECTORY
    
    try:
        # 解析路徑
        resolved_path = str(Path(path).resolve())
        
        # 檢查目錄是否存在
        if not Path(resolved_path).exists():
            return {
                "status": "error",
                "message": f"❌ 目錄不存在：{resolved_path}"
            }
        
        if not Path(resolved_path).is_dir():
            return {
                "status": "error",
                "message": f"❌ 路徑不是目錄：{resolved_path}"
            }
        
        # 更新工作目錄
        WORKING_DIRECTORY = resolved_path
        
        return {
            "status": "success",
            "data": {
                "new_working_directory": WORKING_DIRECTORY
            },
            "message": f"✅ 工作目錄已更改為：{WORKING_DIRECTORY}"
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"❌ 更改工作目錄時發生錯誤：{str(e)}"
        }


@mcp.tool()
def get_directory_info(path: str = None) -> Dict[str, Any]:
    """
    取得目錄資訊和內容列表
    
    參數:
    path (str): 目錄路徑（預設：當前工作目錄）
    
    返回:
    Dict: 包含目錄資訊的字典
    """
    try:
        if path is None:
            path = WORKING_DIRECTORY
        
        path_obj = Path(path)
        
        if not path_obj.exists():
            return {
                "status": "error",
                "message": f"❌ 目錄不存在：{path}"
            }
        
        # 取得目錄內容
        contents = []
        total_size = 0
        
        for item in sorted(path_obj.iterdir()):
            try:
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(item)
                }
                
                if item.is_file():
                    size = item.stat().st_size
                    item_info["size"] = size
                    total_size += size
                
                contents.append(item_info)
            except (PermissionError, OSError):
                # 跳過無法存取的檔案
                continue
        
        return {
            "status": "success",
            "data": {
                "path": str(path_obj.resolve()),
                "total_items": len(contents),
                "directories": len([c for c in contents if c["type"] == "directory"]),
                "files": len([c for c in contents if c["type"] == "file"]),
                "total_size": total_size,
                "contents": contents
            },
            "message": f"✅ 成功取得目錄資訊：{len(contents)} 個項目"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ 取得目錄資訊時發生錯誤：{str(e)}"
        }


@mcp.tool()
def get_git_status() -> Dict[str, Any]:
    """
    取得 Git 狀態資訊
    
    返回:
    Dict: 包含 Git 狀態的字典
    """
    try:
        # 執行 git status
        status_result = execute_command("git status --porcelain", WORKING_DIRECTORY, 10)
        
        if status_result["status"] != "success":
            return status_result
        
        # 解析狀態
        status_lines = status_result["data"]["stdout"].strip().split('\n') if status_result["data"]["stdout"].strip() else []
        
        modified_files = []
        added_files = []
        deleted_files = []
        untracked_files = []
        
        for line in status_lines:
            if len(line) >= 3:
                status_code = line[:2]
                filename = line[3:]
                
                if status_code[0] == 'M' or status_code[1] == 'M':
                    modified_files.append(filename)
                elif status_code[0] == 'A':
                    added_files.append(filename)
                elif status_code[0] == 'D':
                    deleted_files.append(filename)
                elif status_code == '??':
                    untracked_files.append(filename)
        
        # 取得分支資訊
        branch_result = execute_command("git branch --show-current", WORKING_DIRECTORY, 5)
        current_branch = branch_result["data"]["stdout"].strip() if branch_result["status"] == "success" else "unknown"
        
        return {
            "status": "success",
            "data": {
                "current_branch": current_branch,
                "modified_files": modified_files,
                "added_files": added_files, 
                "deleted_files": deleted_files,
                "untracked_files": untracked_files,
                "total_changes": len(modified_files) + len(added_files) + len(deleted_files),
                "is_clean": len(status_lines) == 0
            },
            "message": "✅ Git 狀態檢查完成"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ 取得 Git 狀態時發生錯誤：{str(e)}"
        }


@mcp.tool()
def install_requirements() -> Dict[str, Any]:
    """
    安裝 requirements.txt 中的依賴套件
    
    返回:
    Dict: 包含安裝結果的字典
    """
    try:
        # 檢查 requirements.txt 是否存在
        requirements_path = Path(WORKING_DIRECTORY) / "requirements.txt"
        
        if not requirements_path.exists():
            return {
                "status": "error",
                "message": f"❌ 找不到 requirements.txt 檔案：{requirements_path}"
            }
        
        # 執行 pip install
        return execute_command("pip install -r requirements.txt", WORKING_DIRECTORY, 300)
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ 安裝依賴套件時發生錯誤：{str(e)}"
        }


# 主入口點
def main():
    """啟動 MCP 服務器"""
    # 設定控制台編碼以支援 Unicode
    import sys
    import io
    
    # 確保標準輸出支援 UTF-8
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    try:
        print("🚀 啟動命令執行 MCP 服務器...")
        print(f"📁 預設工作目錄：{WORKING_DIRECTORY}")
        print(f"✅ 允許的命令：{', '.join(ALLOWED_COMMANDS)}")
    except UnicodeEncodeError:
        # 備用方案：使用純文字
        print("[MCP] 啟動命令執行 MCP 服務器...")
        print(f"[DIR] 預設工作目錄：{WORKING_DIRECTORY}")
        print(f"[CMD] 允許的命令：{', '.join(ALLOWED_COMMANDS)}")
    
    mcp.run()


if __name__ == "__main__":
    main()
