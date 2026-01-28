"""
FastAPI后端服务器 - 本地Markdown编辑器
提供文件操作API,支持动态端口分配和Token验证
"""

import os
import sys
import json
import socket
import secrets
import hashlib
import argparse
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 添加mainTools到路径
sys.path.insert(0, os.path.dirname(__file__))
from path_utils import get_posts_path, get_base_path

# 创建FastAPI应用
app = FastAPI(title="Markdown Editor API", version="1.0.0")

# 全局变量
SERVER_PORT = None
AUTH_TOKEN = None

# 并发请求追踪
import threading
active_requests = 0
active_requests_lock = threading.Lock()
MAX_CONCURRENT_REQUESTS = 50  # 最大并发数

@app.middleware("http")
async def track_requests(request, call_next):
    """追踪并发请求数（简化版，无限流）"""
    global active_requests
    
    import time
    request_start = time.time()
    request_id = f"{id(request)}"
    path = request.url.path
    
    print(f"[Middleware-{request_id}] ========== REQUEST START ==========")
    print(f"[Middleware-{request_id}] Path: {path}")
    print(f"[Middleware-{request_id}] Method: {request.method}")
    print(f"[Middleware-{request_id}] Time: {time.strftime('%H:%M:%S')}")
    
    with active_requests_lock:
        active_requests += 1
        current_count = active_requests
    
    print(f"[Middleware-{request_id}] Active requests: {current_count}")
    
    try:
        print(f"[Middleware-{request_id}] Calling next handler...")
        handler_start = time.time()
        response = await call_next(request)
        handler_time = time.time() - handler_start
        
        elapsed = time.time() - request_start
        
        with active_requests_lock:
            active_requests -= 1
            remaining = active_requests
        
        print(f"[Middleware-{request_id}] ========== REQUEST END ==========")
        print(f"[Middleware-{request_id}] Status: {response.status_code}")
        print(f"[Middleware-{request_id}] Handler time: {handler_time*1000:.2f}ms")
        print(f"[Middleware-{request_id}] Total time: {elapsed*1000:.2f}ms")
        print(f"[Middleware-{request_id}] Remaining requests: {remaining}")
        print(f"[Middleware-{request_id}] ==========================================")
        return response
    except Exception as e:
        with active_requests_lock:
            active_requests -= 1
        elapsed = time.time() - request_start
        print(f"[Middleware-{request_id}] ========== REQUEST ERROR ==========")
        print(f"[Middleware-{request_id}] Error: {type(e).__name__}: {e}")
        print(f"[Middleware-{request_id}] Time before error: {elapsed*1000:.2f}ms")
        print(f"[Middleware-{request_id}] ==========================================")
        raise


# ==================== 工具函数 ====================

# Generate 命令异步执行相关
import threading
generate_lock = threading.Lock()
generate_timer = None

def run_generate_command(operation: str = "operation", async_mode: bool = True):
    """
    安全地运行Generate命令，捕获所有异常
    
    Args:
        operation: 操作描述，用于日志
        async_mode: 是否异步执行（默认True）
    """
    def execute_generate():
        try:
            print(f"[API] Running Generate command after {operation}...")
            import time
            start_time = time.time()
            
            from commands import Generate
            generate_cmd = Generate()
            generate_cmd.execute()
            
            elapsed = time.time() - start_time
            print(f"[API] Generate command completed successfully in {elapsed:.2f}s")
        except Exception as e:
            print(f"[API] Warning: Failed to run Generate command after {operation}: {e}")
            import traceback
            traceback.print_exc()
    
    if async_mode:
        # 异步执行，不阻塞API响应
        print(f"[API] Scheduling Generate command (async) after {operation}...")
        thread = threading.Thread(target=execute_generate, daemon=True, name=f"Generate-{operation}")
        thread.start()
    else:
        # 同步执行
        execute_generate()


def run_generate_command_debounced(operation: str = "operation", delay: float = 2.0):
    """
    防抖执行 Generate 命令，在短时间内多次调用只执行最后一次
    
    Args:
        operation: 操作描述，用于日志
        delay: 延迟时间（秒）
    """
    global generate_timer
    
    def execute_generate():
        try:
            print(f"[API] Running Generate command (debounced) after {operation}...")
            import time
            start_time = time.time()
            
            from commands import Generate
            generate_cmd = Generate()
            generate_cmd.execute()
            
            elapsed = time.time() - start_time
            print(f"[API] Generate command (debounced) completed in {elapsed:.2f}s")
        except Exception as e:
            print(f"[API] Warning: Failed to run Generate command (debounced): {e}")
            import traceback
            traceback.print_exc()
    
    with generate_lock:
        if generate_timer:
            print(f"[API] Cancelling previous Generate timer")
            generate_timer.cancel()
        
        print(f"[API] Scheduling Generate command (debounced) in {delay}s...")
        generate_timer = threading.Timer(delay, execute_generate)
        generate_timer.daemon = True
        generate_timer.start()


def find_free_port() -> int:
    """查找可用的随机高端口 (49152-65535)"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def validate_path(path: str) -> str:
    """
    验证路径安全性,防止路径遍历攻击
    
    Args:
        path: 相对于Posts目录的路径
        
    Returns:
        str: 验证后的完整路径
        
    Raises:
        HTTPException: 如果路径不安全或无效
    """
    posts_path = get_posts_path()
    
    # 移除开头的斜杠
    clean_path = path.lstrip('/')
    
    # 规范化路径
    full_path = os.path.normpath(os.path.join(posts_path, clean_path))
    
    # 确保路径在Posts目录内
    if not full_path.startswith(posts_path):
        raise HTTPException(
            status_code=400,
            detail="Invalid path: path traversal detected"
        )
    
    # 确保是.md文件
    if not full_path.endswith('.md'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type: only .md files are allowed"
        )
    
    return full_path


def get_file_version(file_path: str) -> Dict[str, Any]:
    """
    获取文件版本信息
    
    Args:
        file_path: 文件完整路径
        
    Returns:
        dict: 包含lastModified和etag的版本信息
    """
    stat = os.stat(file_path)
    last_modified = int(stat.st_mtime * 1000)  # 转换为毫秒
    
    # 计算ETag (基于内容hash)
    with open(file_path, 'rb') as f:
        content_hash = hashlib.md5(f.read()).hexdigest()
    
    return {
        "lastModified": last_modified,
        "etag": content_hash
    }


# ==================== Token验证中间件 ====================

async def verify_token(x_auth_token: Optional[str] = Header(None)) -> bool:
    """
    验证请求中的Token
    
    Args:
        x_auth_token: 请求头中的Token
        
    Returns:
        bool: 验证成功返回True
        
    Raises:
        HTTPException: Token无效时抛出401错误
    """
    if x_auth_token != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token")
    return True


# ==================== CORS配置 ====================

# 使用正则表达式匹配所有 localhost 端口
# 这个配置允许所有来自 localhost 或 127.0.0.1 的任意端口的请求
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # 预检请求缓存1小时
)


# ==================== Pydantic模型 ====================

class SaveFileRequest(BaseModel):
    """保存文件请求模型"""
    path: str
    content: str
    expectedVersion: Optional[Dict[str, Any]] = None


class CreateFileRequest(BaseModel):
    """创建文件请求模型"""
    path: str
    name: str
    collection: str


class MoveFileRequest(BaseModel):
    """移动文件请求模型"""
    from_path: Optional[str] = None
    to_path: Optional[str] = None
    
    # Also accept 'from' and 'to' as field names
    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }


class RenameRequest(BaseModel):
    """重命名请求模型"""
    path: str
    new_name: str


class CreateFolderRequest(BaseModel):
    """创建文件夹请求模型"""
    path: str
    name: str


# ==================== API端点 ====================

@app.get("/api/health")
async def health_check(authorized: bool = Depends(verify_token)):
    """
    健康检查端点
    用于监控服务器状态
    """
    import time
    start = time.time()
    print(f"[API] HEALTH CHECK - Request received at {time.strftime('%H:%M:%S')}")
    
    # 立即返回，不做任何阻塞操作
    result = {
        "status": "healthy",
        "service": "markdown-editor-api",
        "version": "1.0.0"
    }
    
    elapsed = time.time() - start
    print(f"[API] HEALTH CHECK - Response sent in {elapsed*1000:.2f}ms")
    return result


@app.get("/api/files/tree")
async def get_file_tree(authorized: bool = Depends(verify_token)):
    """
    获取文件树结构 - 异步版本
    
    Returns:
        dict: 包含文件树的JSON结构
    """
    import asyncio
    print("[API] GET FILE TREE - Request received")
    try:
        posts_path = get_posts_path()
        print(f"[API] GET FILE TREE - Posts path: {posts_path}")
        
        if not os.path.exists(posts_path):
            print(f"[API] GET FILE TREE - Posts directory not found!")
            raise HTTPException(status_code=404, detail="Posts directory not found")
        
        def build_tree(directory: str, relative_path: str = "") -> list:
            """递归构建文件树"""
            items = []
            
            try:
                entries = sorted(os.listdir(directory))
            except PermissionError:
                return items
            
            for entry in entries:
                full_path = os.path.join(directory, entry)
                rel_path = os.path.join(relative_path, entry).replace('\\', '/')
                
                if os.path.isdir(full_path):
                    # 跳过Images目录
                    if entry == 'Images':
                        continue
                    
                    # 文件夹节点
                    children = build_tree(full_path, rel_path)
                    items.append({
                        "name": entry,
                        "type": "folder",
                        "path": f"/Posts/{rel_path}",
                        "children": children
                    })
                elif entry.endswith('.md'):
                    # Markdown文件节点
                    items.append({
                        "name": entry,
                        "type": "file",
                        "path": f"/Posts/{rel_path}"
                    })
            
            return items
        
        print("[API] GET FILE TREE - Building tree (async)...")
        # 在线程池中构建文件树，避免阻塞
        loop = asyncio.get_event_loop()
        tree = await loop.run_in_executor(None, build_tree, posts_path)
        print(f"[API] GET FILE TREE - Tree built successfully, {len(tree)} root items")
        
        return {"tree": tree}
        
    except Exception as e:
        print(f"[API] GET FILE TREE - Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to build file tree: {str(e)}"
        )


@app.get("/api/files/read")
async def read_file(path: str, authorized: bool = Depends(verify_token)):
    """
    读取文件内容 - 异步版本
    
    Args:
        path: 文件路径 (相对于Posts目录)
        
    Returns:
        dict: 包含文件内容和版本信息
    """
    import time
    import asyncio
    start = time.time()
    request_id = f"READ-{path[:15]}...{int(time.time()*1000)%10000}"
    
    print(f"\n[{request_id}] ========================================")
    print(f"[{request_id}] READ FILE REQUEST")
    print(f"[{request_id}] Path: {path}")
    print(f"[{request_id}] Time: {time.strftime('%H:%M:%S')}")
    
    try:
        print(f"[{request_id}] Step 1: Validating path...")
        validate_start = time.time()
        full_path = validate_path(path)
        validate_time = time.time() - validate_start
        print(f"[{request_id}] Path validated in {validate_time*1000:.2f}ms")
        print(f"[{request_id}] Full path: {full_path}")
        
        print(f"[{request_id}] Step 2: Checking file existence...")
        exists_start = time.time()
        exists = os.path.exists(full_path)
        exists_time = time.time() - exists_start
        print(f"[{request_id}] Existence check in {exists_time*1000:.2f}ms: {exists}")
        
        if not exists:
            print(f"[{request_id}] ERROR: File not found!")
            raise HTTPException(status_code=404, detail=f"File not found: {path}")
        
        # 使用异步文件读取，不阻塞事件循环
        print(f"[{request_id}] Step 3: Reading file content (async)...")
        print(f"[{request_id}] Getting event loop...")
        loop = asyncio.get_event_loop()
        print(f"[{request_id}] Event loop obtained")
        
        print(f"[{request_id}] Submitting read task to executor...")
        read_start = time.time()
        
        def read_file_sync():
            read_thread_start = time.time()
            print(f"[{request_id}] [THREAD] Starting file read...")
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                read_thread_time = time.time() - read_thread_start
                print(f"[{request_id}] [THREAD] File read complete in {read_thread_time*1000:.2f}ms, size: {len(content)} bytes")
                return content
            except Exception as e:
                print(f"[{request_id}] [THREAD] File read error: {e}")
                raise
        
        content = await loop.run_in_executor(None, read_file_sync)
        read_time = time.time() - read_start
        print(f"[{request_id}] File read completed in {read_time*1000:.2f}ms")
        print(f"[{request_id}] Content length: {len(content)} bytes")
        
        # 获取版本信息（也异步执行）
        print(f"[{request_id}] Step 4: Getting version info (async)...")
        version_start = time.time()
        
        def get_version_sync():
            version_thread_start = time.time()
            print(f"[{request_id}] [THREAD] Getting file version...")
            try:
                version = get_file_version(full_path)
                version_thread_time = time.time() - version_thread_start
                print(f"[{request_id}] [THREAD] Version obtained in {version_thread_time*1000:.2f}ms")
                return version
            except Exception as e:
                print(f"[{request_id}] [THREAD] Version error: {e}")
                raise
        
        version = await loop.run_in_executor(None, get_version_sync)
        version_time = time.time() - version_start
        print(f"[{request_id}] Version info obtained in {version_time*1000:.2f}ms")
        
        elapsed_total = time.time() - start
        print(f"[{request_id}] ========================================")
        print(f"[{request_id}] SUCCESS - Total time: {elapsed_total*1000:.2f}ms")
        print(f"[{request_id}] Breakdown:")
        print(f"[{request_id}]   - Validate: {validate_time*1000:.2f}ms")
        print(f"[{request_id}]   - Exists: {exists_time*1000:.2f}ms")
        print(f"[{request_id}]   - Read: {read_time*1000:.2f}ms")
        print(f"[{request_id}]   - Version: {version_time*1000:.2f}ms")
        print(f"[{request_id}] ========================================\n")
        
        return {
            "content": content,
            "version": version
        }
        
    except HTTPException:
        raise
    except Exception as e:
        elapsed = time.time() - start
        print(f"[{request_id}] ========================================")
        print(f"[{request_id}] ERROR after {elapsed*1000:.2f}ms")
        print(f"[{request_id}] Exception: {type(e).__name__}: {e}")
        print(f"[{request_id}] ========================================\n")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read file: {str(e)}"
        )


@app.post("/api/files/save")
async def save_file(data: SaveFileRequest, authorized: bool = Depends(verify_token)):
    """
    保存文件内容 - 异步版本
    
    Args:
        data: 包含路径、内容和期望版本的请求数据
        
    Returns:
        dict: 保存结果和新版本信息
    """
    import asyncio
    print(f"[API] SAVE FILE - Request received for path: {data.path}")
    print(f"[API] SAVE FILE - Content length: {len(data.content)} bytes")
    try:
        full_path = validate_path(data.path)
        print(f"[API] SAVE FILE - Validated full path: {full_path}")
        
        # 版本冲突检测（异步）
        loop = asyncio.get_event_loop()
        if os.path.exists(full_path) and data.expectedVersion:
            print(f"[API] SAVE FILE - Checking version conflict...")
            current_version = await loop.run_in_executor(None, get_file_version, full_path)
            expected = data.expectedVersion
            
            if (current_version['lastModified'] != expected.get('lastModified') or
                current_version['etag'] != expected.get('etag')):
                print(f"[API] SAVE FILE - Version conflict detected!")
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error": "version_conflict",
                        "message": "File has been modified by another process",
                        "currentVersion": current_version
                    }
                )
        
        # 确保目录存在
        await loop.run_in_executor(None, lambda: os.makedirs(os.path.dirname(full_path), exist_ok=True))
        
        # 保存文件（异步）
        print(f"[API] SAVE FILE - Writing file (async)...")
        def write_file():
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(data.content)
        
        await loop.run_in_executor(None, write_file)
        print(f"[API] SAVE FILE - File written successfully")
        
        # 获取新版本信息（异步）
        new_version = await loop.run_in_executor(None, get_file_version, full_path)
        print(f"[API] SAVE FILE - New version: {new_version}")
        
        print(f"[API] SAVE FILE - Success")
        return {
            "success": True,
            "message": "File saved successfully",
            "version": new_version
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] SAVE FILE - Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )


@app.post("/api/files/create")
async def create_file(data: CreateFileRequest, authorized: bool = Depends(verify_token)):
    """
    创建新文件
    
    Args:
        data: 包含路径、名称和集合的请求数据
        
    Returns:
        dict: 创建结果
    """
    try:
        full_path = validate_path(data.path)
        
        # 检查文件是否已存在
        if os.path.exists(full_path):
            raise HTTPException(
                status_code=400,
                detail=f"File already exists: {data.path}"
            )
        
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # 生成默认front-matter
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        metadata = f"""---
title: {data.name}
date: {date_str}
tags: 
categories: 
pre: 
img: 
---

"""
        
        # 创建文件
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(metadata)
        
        # 调用Generate命令更新配置（防抖模式）
        run_generate_command_debounced("file creation", delay=1.0)
        
        return {
            "success": True,
            "message": "File created successfully",
            "path": data.path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create file: {str(e)}"
        )


@app.delete("/api/files/delete")
async def delete_file(path: str, authorized: bool = Depends(verify_token)):
    """
    删除文件
    
    Args:
        path: 文件路径 (相对于Posts目录)
        
    Returns:
        dict: 删除结果
    """
    try:
        full_path = validate_path(path)
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File not found: {path}")
        
        # 删除文件
        os.remove(full_path)
        
        # 调用Generate命令更新配置（防抖模式）
        run_generate_command_debounced("file deletion", delay=1.0)
        
        return {
            "success": True,
            "message": "File deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )


@app.post("/api/files/move")
async def move_file(data: MoveFileRequest, authorized: bool = Depends(verify_token)):
    """
    移动文件 - 集成MovePost命令逻辑
    
    Args:
        data: 包含源路径和目标路径的请求数据
        
    Returns:
        dict: 移动结果
    """
    try:
        # Support both 'from'/'to' and 'from_path'/'to_path' field names
        from_path = data.from_path or getattr(data, 'from', None) or data.model_extra.get('from') if hasattr(data, 'model_extra') and data.model_extra else None
        to_path = data.to_path or getattr(data, 'to', None) or data.model_extra.get('to') if hasattr(data, 'model_extra') and data.model_extra else None
        
        # Fallback: check model_extra for 'from' and 'to'
        if not from_path and hasattr(data, 'model_extra') and data.model_extra:
            from_path = data.model_extra.get('from')
        if not to_path and hasattr(data, 'model_extra') and data.model_extra:
            to_path = data.model_extra.get('to')
        
        if not from_path or not to_path:
            raise HTTPException(
                status_code=400,
                detail="Both 'from' and 'to' paths are required"
            )
        
        # 验证路径
        full_from_path = validate_path(from_path)
        full_to_path = validate_path(to_path)
        
        if not os.path.exists(full_from_path):
            raise HTTPException(status_code=404, detail=f"Source file not found: {from_path}")
        
        # 解析路径以提取文件名和集合信息
        posts_path = get_posts_path()
        
        # 提取源文件信息
        rel_from_path = os.path.relpath(full_from_path, posts_path)
        from_parts = rel_from_path.replace('\\', '/').split('/')
        post_name = os.path.splitext(from_parts[-1])[0]  # 移除.md后缀
        source_collection = from_parts[0] if len(from_parts) > 1 else 'Markdowns'
        
        # 提取目标集合信息
        rel_to_path = os.path.relpath(full_to_path, posts_path)
        to_parts = rel_to_path.replace('\\', '/').split('/')
        target_collection = to_parts[0] if len(to_parts) > 1 else 'Markdowns'
        
        # 使用MovePost命令执行移动操作
        try:
            from move_post_command import MovePost
            move_cmd = MovePost()
            result = move_cmd.execute(post_name, source_collection, target_collection)
            
            if not result['success']:
                raise HTTPException(
                    status_code=400,
                    detail=result['message']
                )
            
            # 调用Generate命令更新配置（防抖模式）
            run_generate_command_debounced("file move", delay=1.0)
            
            return {
                "success": True,
                "message": result['message']
            }
            
        except ImportError as e:
            # 如果MovePost命令不可用,回退到基本的文件移动
            print(f"Warning: MovePost command not available, using fallback: {e}")
            
            if os.path.exists(full_to_path):
                raise HTTPException(
                    status_code=400,
                    detail=f"Destination file already exists: {to_path}"
                )
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(full_to_path), exist_ok=True)
            
            # 移动文件
            os.rename(full_from_path, full_to_path)
            
            # 调用Generate命令更新配置（防抖模式）
            run_generate_command_debounced("file move (fallback)", delay=1.0)
            
            return {
                "success": True,
                "message": "File moved successfully"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to move file: {str(e)}"
        )


@app.post("/api/files/rename")
async def rename_file_or_folder(data: RenameRequest, authorized: bool = Depends(verify_token)):
    """
    重命名文件或文件夹
    
    Args:
        data: 包含路径和新名称的请求数据
        
    Returns:
        dict: 重命名结果
    """
    try:
        # 验证路径（对于文件夹，暂时跳过.md检查）
        posts_path = get_posts_path()
        clean_path = data.path.lstrip('/')
        full_path = os.path.normpath(os.path.join(posts_path, clean_path))
        
        # 确保路径在Posts目录内
        if not full_path.startswith(posts_path):
            raise HTTPException(
                status_code=400,
                detail="Invalid path: path traversal detected"
            )
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File or folder not found: {data.path}")
        
        # 构建新路径
        parent_dir = os.path.dirname(full_path)
        is_file = os.path.isfile(full_path)
        
        # 如果是文件，确保新名称有.md扩展名
        if is_file:
            new_name = data.new_name if data.new_name.endswith('.md') else f"{data.new_name}.md"
        else:
            new_name = data.new_name
        
        new_path = os.path.join(parent_dir, new_name)
        
        # 检查新路径是否已存在
        if os.path.exists(new_path):
            raise HTTPException(
                status_code=400,
                detail=f"A file or folder with name '{new_name}' already exists"
            )
        
        # 执行重命名
        os.rename(full_path, new_path)
        
        # 调用Generate命令更新配置（防抖模式）
        run_generate_command_debounced("rename", delay=1.0)
        
        return {
            "success": True,
            "message": f"{'File' if is_file else 'Folder'} renamed successfully",
            "new_path": os.path.relpath(new_path, posts_path).replace('\\', '/')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to rename: {str(e)}"
        )


@app.post("/api/folders/create")
async def create_folder(data: CreateFolderRequest, authorized: bool = Depends(verify_token)):
    """
    创建文件夹
    
    Args:
        data: 包含父路径和文件夹名称的请求数据
        
    Returns:
        dict: 创建结果
    """
    try:
        posts_path = get_posts_path()
        
        # 验证父路径
        clean_parent_path = data.path.lstrip('/')
        parent_full_path = os.path.normpath(os.path.join(posts_path, clean_parent_path))
        
        # 确保父路径在Posts目录内
        if not parent_full_path.startswith(posts_path):
            raise HTTPException(
                status_code=400,
                detail="Invalid path: path traversal detected"
            )
        
        # 如果父路径不存在，创建它
        if not os.path.exists(parent_full_path):
            os.makedirs(parent_full_path, exist_ok=True)
        
        # 构建新文件夹路径
        new_folder_path = os.path.join(parent_full_path, data.name)
        
        # 检查文件夹是否已存在
        if os.path.exists(new_folder_path):
            raise HTTPException(
                status_code=400,
                detail=f"Folder '{data.name}' already exists"
            )
        
        # 创建文件夹
        os.makedirs(new_folder_path, exist_ok=True)
        
        # 调用Generate命令更新配置（防抖模式）
        run_generate_command_debounced("folder creation", delay=1.0)
        
        return {
            "success": True,
            "message": "Folder created successfully",
            "path": os.path.relpath(new_folder_path, posts_path).replace('\\', '/')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create folder: {str(e)}"
        )


@app.delete("/api/folders/delete")
async def delete_folder(path: str, authorized: bool = Depends(verify_token)):
    """
    删除文件夹及其所有内容
    
    Args:
        path: 要删除的文件夹路径（相对于Posts目录）
        
    Returns:
        dict: 删除结果
    """
    try:
        posts_path = get_posts_path()
        
        # 验证路径
        clean_path = path.lstrip('/')
        full_path = os.path.normpath(os.path.join(posts_path, clean_path))
        
        # 确保路径在Posts目录内
        if not full_path.startswith(posts_path):
            raise HTTPException(
                status_code=400,
                detail="Invalid path: path traversal detected"
            )
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"Folder not found: {path}")
        
        if not os.path.isdir(full_path):
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a folder: {path}"
            )
        
        # 防止删除特殊文件夹
        folder_name = os.path.basename(full_path)
        if folder_name in ['Markdowns', 'Images']:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete system folder: {folder_name}"
            )
        
        # 删除文件夹及其所有内容
        import shutil
        shutil.rmtree(full_path)
        
        print(f"[API] Folder deleted: {path}")
        
        # 调用Generate命令更新配置（防抖模式）
        run_generate_command_debounced("folder deletion", delay=1.0)
        
        return {
            "success": True,
            "message": "Folder deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete folder: {str(e)}"
        )


# 图片上传API
from fastapi import File, UploadFile, Form

@app.post("/api/images/upload")
async def upload_image_handler(
    image: UploadFile = File(...),
    article_name: str = Form(...),
    authorized: bool = Depends(verify_token)
):
    """
    上传图片到Images目录
    
    接收multipart/form-data格式的图片文件
    自动按文章名分类存储，并按数字递增命名
    
    Args:
        image: 图片文件
        article_name: 文章名（不含.md扩展名）
        
    Returns:
        dict: 包含图片相对路径的结果
    """
    try:
        print(f"[API] IMAGE UPLOAD - Request received")
        print(f"[API] IMAGE UPLOAD - Article name: {article_name}")
        print(f"[API] IMAGE UPLOAD - File name: {image.filename}")
        print(f"[API] IMAGE UPLOAD - Content type: {image.content_type}")
        
        # 验证文件类型
        allowed_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type: {image.content_type}. Allowed types: {', '.join(allowed_types)}"
            )
        
        # 获取文件扩展名
        file_ext = os.path.splitext(image.filename)[1].lower()
        if not file_ext:
            # 根据content_type推断扩展名
            ext_map = {
                'image/png': '.png',
                'image/jpeg': '.jpg',
                'image/jpg': '.jpg',
                'image/gif': '.gif',
                'image/webp': '.webp'
            }
            file_ext = ext_map.get(image.content_type, '.png')
        
        # 构建目标目录路径
        posts_path = get_posts_path()
        images_base = os.path.join(posts_path, 'Images')
        article_images_dir = os.path.join(images_base, article_name)
        
        # 确保目录存在
        os.makedirs(article_images_dir, exist_ok=True)
        print(f"[API] IMAGE UPLOAD - Target directory: {article_images_dir}")
        
        # 查找下一个可用的数字
        existing_files = []
        if os.path.exists(article_images_dir):
            existing_files = [f for f in os.listdir(article_images_dir) 
                            if os.path.isfile(os.path.join(article_images_dir, f))]
        
        # 提取现有文件的数字
        existing_numbers = []
        for filename in existing_files:
            name_without_ext = os.path.splitext(filename)[0]
            if name_without_ext.isdigit():
                existing_numbers.append(int(name_without_ext))
        
        # 确定新文件的数字
        next_number = 1
        if existing_numbers:
            next_number = max(existing_numbers) + 1
        
        # 构建新文件名
        new_filename = f"{next_number}{file_ext}"
        target_path = os.path.join(article_images_dir, new_filename)
        
        print(f"[API] IMAGE UPLOAD - New filename: {new_filename}")
        print(f"[API] IMAGE UPLOAD - Target path: {target_path}")
        
        # 保存文件
        content = await image.read()
        with open(target_path, 'wb') as f:
            f.write(content)
        
        print(f"[API] IMAGE UPLOAD - File saved successfully")
        print(f"[API] IMAGE UPLOAD - File size: {len(content)} bytes")
        
        # 返回相对路径（相对于Images目录）
        relative_path = f"{article_name}/{new_filename}"
        
        print(f"[API] IMAGE UPLOAD - Relative path: {relative_path}")
        
        return {
            "success": True,
            "message": "Image uploaded successfully",
            "path": relative_path,
            "filename": new_filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] IMAGE UPLOAD - Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )


# ==================== 服务器启动 ====================

def main():
    """主函数 - 启动服务器"""
    global SERVER_PORT, AUTH_TOKEN
    
    # 配置 logging 避免 formatter 错误
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Markdown Editor API Server')
    parser.add_argument('--info-file', type=str, help='Path to write server info JSON')
    args = parser.parse_args()
    
    # 生成随机端口和token
    SERVER_PORT = find_free_port()
    AUTH_TOKEN = secrets.token_urlsafe(32)
    
    # 如果指定了info文件,写入服务器信息
    if args.info_file:
        server_info = {
            'port': SERVER_PORT,
            'token': AUTH_TOKEN
        }
        with open(args.info_file, 'w') as f:
            json.dump(server_info, f)
    
    # 打印服务器信息
    print(f"=" * 60)
    print(f"Markdown Editor API Server")
    print(f"=" * 60)
    print(f"Port: {SERVER_PORT}")
    print(f"Token: {AUTH_TOKEN}")
    print(f"Health Check: http://127.0.0.1:{SERVER_PORT}/api/health")
    print(f"=" * 60)
    
    # 启动服务器 - 使用多worker和异步配置
    import uvicorn
    
    # 配置说明：
    # - workers=1: 单worker但使用异步事件循环
    # - limit_concurrency=200: 每个worker最多200个并发连接
    # - timeout_keep_alive=30: 保持连接30秒
    # - backlog=2048: 等待队列大小
    
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=SERVER_PORT,
            log_level="info",
            workers=1,
            limit_concurrency=200,
            timeout_keep_alive=30,
            backlog=2048,
            loop="asyncio"
        )
    except Exception as e:
        # 如果启动失败，尝试使用最小配置
        print(f"⚠️ 服务器启动失败，尝试使用简化配置: {e}")
        print(f"正在使用最小配置重新启动...")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=SERVER_PORT,
            access_log=False  # 禁用访问日志避免 formatter 问题
        )


if __name__ == "__main__":
    main()
