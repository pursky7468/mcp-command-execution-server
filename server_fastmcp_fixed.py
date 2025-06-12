#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server for Command Execution Tools (修正 Windows 編碼問題)

解決 Windows 中文編碼問題的命令執行工具
"""

import subprocess
import os
import sys
import locale
from pathlib import Path
from typing import Dict, Any, List

from fastmcp import FastMCP

# 建立 FastMCP 實例
mcp = FastMCP("command-execution-server")

# 全域配置
WORKING_DIRECTORY = r"C:\Users\User\Desktop\LineBot"
ALLOWED_COMMANDS = [
    "python", "pip", "git", "dir", "ls", "cd", "mkdir", 
    "copy", "move", "del", "type", "cat", "cls", "clear", "chcp"
]

# Windows 編碼處理
def get_system_encoding():
    """取得系統編碼"""
    try:
        # 嘗試取得 Windows 控制台編碼
        result = subprocess.run(['chcp'], capture_output=True, text=True, shell=True)
        if result.returncode == 0 and 'Active code page:' in result.stdout:
            # 提取編碼頁碼
            codepage = result.stdout.split(':')[-1].strip()
            if codepage == '950':
                return 'big5'
            elif codepage == '936':
                return 'gbk'
            elif codepage == '65001':
                return 'utf-8'
        
        # 備用方案
        return locale.getpreferredencoding()
    except:
        return 'utf-8'

SYSTEM_ENCODING = get_system_encoding()

# ===== 改善的命令執行工具 =====

@mcp.tool(
    description="""
    執行系統命令（修正編碼問題）
    
    參數:
    command (str): 要執行的命令
    working_directory (str): 工作目錄（預設：LineBot 專案目錄）
    timeout (int): 超時時間（秒，預設：30）
    
    返回:
    Dict: 包含執行結果的字典
    """
)
def execute_command(command: str, working_directory: str = WORKING_DIRECTORY, timeout: int = 30) -> Dict[str, Any]:
    """
    執行系統命令（修正編碼問題）
    
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
        
        # 修正：根據系統編碼執行命令
        try:
            # 首先嘗試 UTF-8
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
        except UnicodeDecodeError:
            # 如果 UTF-8 失敗，使用系統編碼
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_directory,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding=SYSTEM_ENCODING,
                errors='replace'
            )
        
        # 清理輸出文字
        stdout_clean = result.stdout.replace('\r\n', '\n').replace('\r', '\n')
        stderr_clean = result.stderr.replace('\r\n', '\n').replace('\r', '\n')
        
        return {
            "status": "success",
            "data": {
                "command": command,
                "working_directory": working_directory,
                "exit_code": result.returncode,
                "stdout": stdout_clean,
                "stderr": stderr_clean,
                "success": result.returncode == 0,
                "encoding_used": SYSTEM_ENCODING
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


@mcp.tool(
    description="""
    安全的目錄列表功能（使用 Python 而非系統命令）
    
    參數:
    path (str): 目錄路徑（預設：當前工作目錄）
    
    返回:
    Dict: 包含目錄資訊的字典
    """
)
def list_directory_safe(path: str = None) -> Dict[str, Any]:
    """
    安全的目錄列表功能（使用 Python 而非系統命令）
    
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
        
        # 使用 Python 直接列出目錄內容（避免編碼問題）
        contents = []
        total_size = 0
        dir_count = 0
        file_count = 0
        
        for item in sorted(path_obj.iterdir()):
            try:
                item_info = {
                    "name": item.name,
                    "type": "📁" if item.is_dir() else "📄",
                    "is_directory": item.is_dir(),
                    "path": str(item)
                }
                
                if item.is_dir():
                    dir_count += 1
                    try:
                        # 計算目錄中的項目數
                        sub_items = len(list(item.iterdir()))
                        item_info["items"] = sub_items
                    except (PermissionError, OSError):
                        item_info["items"] = "無法存取"
                else:
                    file_count += 1
                    try:
                        size = item.stat().st_size
                        item_info["size"] = size
                        item_info["size_readable"] = format_size(size)
                        total_size += size
                    except (PermissionError, OSError):
                        item_info["size"] = "無法存取"
                        item_info["size_readable"] = "無法存取"
                
                contents.append(item_info)
            except (PermissionError, OSError) as e:
                # 添加無法存取的項目資訊
                contents.append({
                    "name": item.name,
                    "type": "❌",
                    "error": f"無法存取: {str(e)}"
                })
                continue
        
        return {
            "status": "success",
            "data": {
                "path": str(path_obj.resolve()),
                "total_items": len(contents),
                "directories": dir_count,
                "files": file_count,
                "total_size": total_size,
                "total_size_readable": format_size(total_size),
                "contents": contents
            },
            "message": f"✅ 成功取得目錄資訊：{len(contents)} 個項目（📁{dir_count} 目錄，📄{file_count} 檔案）"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ 取得目錄資訊時發生錯誤：{str(e)}"
        }


def format_size(size_bytes: int) -> str:
    """格式化檔案大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


@mcp.tool(
    description="""
    在 LineBot 專案目錄中執行 Python 腳本
    
    參數:
    script_name (str): Python 腳本名稱（如 'test_architecture.py'）
    args (List[str]): 命令列參數（可選）
    timeout (int): 超時時間（秒，預設：60）
    
    返回:
    Dict: 包含執行結果的字典
    """
)
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
        
        # 使用改善的 execute_command 函數
        return execute_command(command, WORKING_DIRECTORY, timeout)
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ 執行 Python 腳本時發生錯誤：{str(e)}"
        }


@mcp.tool(
    description="""
    檢查 Python 環境和相關資訊
    
    返回:
    Dict: 包含 Python 環境資訊的字典
    """
)
def check_python_environment() -> Dict[str, Any]:
    """
    檢查 Python 環境和相關資訊
    
    返回:
    Dict: 包含 Python 環境資訊的字典
    """
    try:
        # 檢查 Python 版本
        python_version = execute_command("python --version", WORKING_DIRECTORY, 10)
        
        # 檢查 pip 版本
        pip_version = execute_command("pip --version", WORKING_DIRECTORY, 10)
        
        # 檢查已安裝的套件
        pip_list = execute_command("pip list --format=freeze", WORKING_DIRECTORY, 30)
        
        # 檢查是否有 requirements.txt
        requirements_path = Path(WORKING_DIRECTORY) / "requirements.txt"
        has_requirements = requirements_path.exists()
        
        environment_info = {
            "python_version": python_version["data"] if python_version["status"] == "success" else "無法取得",
            "pip_version": pip_version["data"] if pip_version["status"] == "success" else "無法取得",
            "has_requirements_txt": has_requirements,
            "working_directory": WORKING_DIRECTORY,
            "system_encoding": SYSTEM_ENCODING
        }
        
        if pip_list["status"] == "success":
            installed_packages = pip_list["data"]["stdout"].strip().split('\n')
            environment_info["installed_packages_count"] = len([p for p in installed_packages if p.strip()])
            environment_info["sample_packages"] = installed_packages[:10]  # 顯示前10個套件
        
        return {
            "status": "success",
            "data": environment_info,
            "message": "✅ Python 環境檢查完成"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ 檢查 Python 環境時發生錯誤：{str(e)}"
        }


@mcp.tool(
    description="""
    取得 Git 狀態資訊
    
    返回:
    Dict: 包含 Git 狀態的字典
    """
)
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


@mcp.tool(
    description="""
    安裝 requirements.txt 中的依賴套件
    
    返回:
    Dict: 包含安裝結果的字典
    """
)
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
    try:
        print("🚀 啟動命令執行 MCP 服務器（修正編碼版本）...")
        print(f"📁 預設工作目錄：{WORKING_DIRECTORY}")
        print(f"🔤 系統編碼：{SYSTEM_ENCODING}")
        print(f"✅ 允許的命令：{', '.join(ALLOWED_COMMANDS)}")
    except Exception as e:
        print(f"[MCP] 啟動命令執行 MCP 服務器（修正編碼版本）...")
        print(f"[DIR] 預設工作目錄：{WORKING_DIRECTORY}")
        print(f"[ENC] 系統編碼：{SYSTEM_ENCODING}")
    
    mcp.run()


if __name__ == "__main__":
    main()
