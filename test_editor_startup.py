"""
测试编辑器启动脚本
用于调试编辑器启动问题
"""

import os
import sys
import subprocess
import time
import json
import tempfile

def test_editor_startup():
    """测试编辑器启动流程"""
    
    print("=" * 60)
    print("测试编辑器启动")
    print("=" * 60)
    
    # 创建临时文件
    info_file = tempfile.NamedTemporaryFile(
        mode='w', 
        delete=False, 
        suffix='.json'
    )
    info_path = info_file.name
    info_file.close()
    
    print(f"临时文件路径: {info_path}")
    
    # 获取服务器脚本路径
    server_script = os.path.join(
        os.path.dirname(__file__), 
        'mainTools', 
        'editor_server.py'
    )
    
    print(f"服务器脚本: {server_script}")
    print(f"Python解释器: {sys.executable}")
    
    # 启动服务器
    print("\n启动服务器...")
    process = subprocess.Popen(
        [sys.executable, server_script, "--info-file", info_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False
    )
    
    print(f"进程ID: {process.pid}")
    
    # 等待服务器启动
    max_wait = 20
    server_info = None
    
    for i in range(max_wait):
        time.sleep(0.5)
        
        # 检查进程状态
        poll_result = process.poll()
        if poll_result is not None:
            print(f"\n❌ 进程已退出 (退出码: {poll_result})")
            stderr = process.stderr.read().decode('utf-8', errors='ignore')
            stdout = process.stdout.read().decode('utf-8', errors='ignore')
            
            if stdout:
                print(f"\n标准输出:\n{stdout}")
            if stderr:
                print(f"\n错误输出:\n{stderr}")
            
            return False
        
        # 检查信息文件
        if os.path.exists(info_path):
            file_size = os.path.getsize(info_path)
            print(f"[{i+1}/{max_wait}] 信息文件存在, 大小: {file_size} 字节")
            
            if file_size > 0:
                try:
                    with open(info_path, 'r') as f:
                        server_info = json.load(f)
                    print(f"\n✓ 成功读取服务器信息!")
                    print(f"  端口: {server_info['port']}")
                    print(f"  Token: {server_info['token'][:20]}...")
                    break
                except json.JSONDecodeError as e:
                    print(f"[{i+1}/{max_wait}] JSON解析失败: {e}")
                except Exception as e:
                    print(f"[{i+1}/{max_wait}] 读取失败: {e}")
        else:
            print(f"[{i+1}/{max_wait}] 等待信息文件...")
    
    if server_info is None:
        print("\n❌ 超时: 未能获取服务器信息")
        
        # 尝试读取输出
        try:
            stderr = process.stderr.read().decode('utf-8', errors='ignore')
            stdout = process.stdout.read().decode('utf-8', errors='ignore')
            
            if stdout:
                print(f"\n标准输出:\n{stdout}")
            if stderr:
                print(f"\n错误输出:\n{stderr}")
        except:
            pass
        
        # 终止进程
        process.terminate()
        return False
    
    # 测试健康检查
    print("\n测试健康检查...")
    try:
        import requests
        response = requests.get(
            f"http://127.0.0.1:{server_info['port']}/api/health",
            headers={"X-Auth-Token": server_info['token']},
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✓ 健康检查成功: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    # 清理
    print("\n清理...")
    process.terminate()
    process.wait(timeout=5)
    
    try:
        os.unlink(info_path)
    except:
        pass
    
    print("\n✓ 测试完成!")
    return True


if __name__ == "__main__":
    success = test_editor_startup()
    sys.exit(0 if success else 1)
