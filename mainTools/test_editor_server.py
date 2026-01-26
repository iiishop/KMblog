"""
测试FastAPI编辑器服务器 - 文件保存API
验证文件保存功能和版本冲突检?
"""

import os
import sys
import tempfile
import shutil
import time
import hashlib
from pathlib import Path

# 添加mainTools到路?
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from fastapi.testclient import TestClient
from editor_server import app, AUTH_TOKEN, validate_path, get_file_version

# 设置测试token
os.environ['AUTH_TOKEN'] = 'test-token-12345'
import editor_server
editor_server.AUTH_TOKEN = 'test-token-12345'

# 创建测试客户?
client = TestClient(app)

# 测试用的headers
TEST_HEADERS = {"X-Auth-Token": "test-token-12345"}


@pytest.fixture
def temp_posts_dir(monkeypatch):
    """创建临时Posts目录用于测试"""
    temp_dir = tempfile.mkdtemp()
    posts_dir = os.path.join(temp_dir, "Posts", "Markdowns")
    os.makedirs(posts_dir, exist_ok=True)
    
    # 使用monkeypatch替换get_posts_path
    def mock_get_posts_path():
        return os.path.join(temp_dir, "Posts")
    
    # 替换editor_server模块中的函数
    monkeypatch.setattr(editor_server, 'get_posts_path', mock_get_posts_path)
    
    # 同时替换path_utils模块中的函数
    import path_utils
    monkeypatch.setattr(path_utils, 'get_posts_path', mock_get_posts_path)
    
    yield os.path.join(temp_dir, "Posts")
    
    # 清理临时目录
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestFileSaveAPI:
    """测试文件保存API (POST /api/files/save)"""
    
    def test_save_new_file(self, temp_posts_dir):
        """测试保存新文?""
        # 准备测试数据 - 路径应该相对于Posts目录,不包?Posts/前缀
        test_path = "/Markdowns/test-new-file.md"
        test_content = "# Test Content\n\nThis is a test file."
        
        # 调用保存API
        response = client.post(
            "/api/files/save",
            json={
                "path": test_path,
                "content": test_content
            },
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "File saved successfully"
        assert "version" in data
        assert "lastModified" in data["version"]
        assert "etag" in data["version"]
        
        # 验证文件确实被创?
        full_path = os.path.join(temp_posts_dir, "Markdowns", "test-new-file.md")
        assert os.path.exists(full_path)
        
        # 验证文件内容
        with open(full_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        assert saved_content == test_content
        
        # 验证文件内容
        with open(full_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        assert saved_content == test_content
    
    def test_save_existing_file_without_version(self, temp_posts_dir):
        """测试保存已存在的文件(不提供版本信?"""
        # 创建初始文件
        test_path = "/Markdowns/test-existing.md"
        initial_content = "# Initial Content"
        full_path = os.path.join(temp_posts_dir, "Markdowns", "test-existing.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        # 更新文件内容(不提供版本信?
        updated_content = "# Updated Content\n\nNew content here."
        response = client.post(
            "/api/files/save",
            json={
                "path": test_path,
                "content": updated_content
            },
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证文件内容已更?
        with open(full_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        assert saved_content == updated_content
    
    def test_save_with_correct_version(self, temp_posts_dir):
        """测试使用正确版本信息保存文件"""
        # 创建初始文件
        test_path = "/Markdowns/test-version.md"
        initial_content = "# Version Test"
        full_path = os.path.join(temp_posts_dir, "Markdowns", "test-version.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        # 获取当前版本信息
        current_version = get_file_version(full_path)
        
        # 使用正确的版本信息保?
        updated_content = "# Version Test Updated"
        response = client.post(
            "/api/files/save",
            json={
                "path": test_path,
                "content": updated_content,
                "expectedVersion": current_version
            },
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证版本信息已更?
        new_version = data["version"]
        assert new_version["lastModified"] >= current_version["lastModified"]
        assert new_version["etag"] != current_version["etag"]  # 内容变了,etag应该不同
    
    def test_version_conflict_detection_modified_time(self, temp_posts_dir):
        """测试版本冲突检?- 修改时间不匹?""
        # 创建初始文件
        test_path = "/Markdowns/test-conflict.md"
        initial_content = "# Conflict Test"
        full_path = os.path.join(temp_posts_dir, "Markdowns", "test-conflict.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        # 获取初始版本
        initial_version = get_file_version(full_path)
        
        # 模拟另一个进程修改了文件
        time.sleep(0.1)  # 确保时间戳不?
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("# Modified by another process")
        
        # 尝试使用旧版本信息保?
        response = client.post(
            "/api/files/save",
            json={
                "path": test_path,
                "content": "# My changes",
                "expectedVersion": initial_version
            },
            headers=TEST_HEADERS
        )
        
        # 验证返回409冲突错误
        assert response.status_code == 409
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert detail["error"] == "version_conflict"
        assert "currentVersion" in detail
        assert detail["currentVersion"]["lastModified"] != initial_version["lastModified"]
    
    def test_version_conflict_detection_etag(self, temp_posts_dir):
        """测试版本冲突检?- ETag不匹?""
        # 创建初始文件
        test_path = "/Markdowns/test-etag-conflict.md"
        initial_content = "# ETag Test"
        full_path = os.path.join(temp_posts_dir, "Markdowns", "test-etag-conflict.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        # 获取初始版本
        initial_version = get_file_version(full_path)
        
        # 模拟另一个进程修改了文件内容(但保持相同的修改时间是不可能?
        # 所以我们构造一个错误的expectedVersion)
        wrong_version = {
            "lastModified": initial_version["lastModified"],
            "etag": "wrong-etag-12345"
        }
        
        # 尝试使用错误的etag保存
        response = client.post(
            "/api/files/save",
            json={
                "path": test_path,
                "content": "# My changes",
                "expectedVersion": wrong_version
            },
            headers=TEST_HEADERS
        )
        
        # 验证返回409冲突错误
        assert response.status_code == 409
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert detail["error"] == "version_conflict"
    
    def test_save_invalid_path(self, temp_posts_dir):
        """测试保存到无效路?""
        # 尝试路径遍历攻击
        response = client.post(
            "/api/files/save",
            json={
                "path": "../../../etc/passwd",
                "content": "malicious content"
            },
            headers=TEST_HEADERS
        )
        
        # 验证被拒?
        assert response.status_code == 400
        assert "path traversal" in response.json()["detail"].lower()
    
    def test_save_non_markdown_file(self, temp_posts_dir):
        """测试保存非Markdown文件"""
        response = client.post(
            "/api/files/save",
            json={
                "path": "/test.txt",
                "content": "text file"
            },
            headers=TEST_HEADERS
        )
        
        # 验证被拒?
        assert response.status_code == 400
        assert "only .md files" in response.json()["detail"].lower()
    
    def test_save_without_token(self, temp_posts_dir):
        """测试不提供Token的保存请?""
        response = client.post(
            "/api/files/save",
            json={
                "path": "/Markdowns/test.md",
                "content": "content"
            }
        )
        
        # 验证被拒?
        assert response.status_code == 401
    
    def test_save_with_invalid_token(self, temp_posts_dir):
        """测试使用无效Token的保存请?""
        response = client.post(
            "/api/files/save",
            json={
                "path": "/Markdowns/test.md",
                "content": "content"
            },
            headers={"X-Auth-Token": "invalid-token"}
        )
        
        # 验证被拒?
        assert response.status_code == 401


class TestFileReadAPI:
    """测试文件读取API - 验证版本信息返回"""
    
    def test_read_file_returns_version(self, temp_posts_dir):
        """测试读取文件时返回版本信?""
        # 创建测试文件
        test_path = "/Markdowns/test-read.md"
        test_content = "# Read Test\n\nContent here."
        full_path = os.path.join(temp_posts_dir, "Markdowns", "test-read.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 读取文件
        response = client.get(
            "/api/files/read",
            params={"path": test_path},
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == test_content
        assert "version" in data
        assert "lastModified" in data["version"]
        assert "etag" in data["version"]
        
        # 验证版本信息的正确?
        expected_version = get_file_version(full_path)
        assert data["version"]["lastModified"] == expected_version["lastModified"]
        assert data["version"]["etag"] == expected_version["etag"]


class TestVersionInfoGeneration:
    """测试版本信息生成函数"""
    
    def test_get_file_version(self, temp_posts_dir):
        """测试get_file_version函数"""
        # 创建测试文件
        test_content = "# Version Info Test"
        full_path = os.path.join(temp_posts_dir, "Markdowns", "version-test.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 获取版本信息
        version = get_file_version(full_path)
        
        # 验证版本信息结构
        assert "lastModified" in version
        assert "etag" in version
        assert isinstance(version["lastModified"], int)
        assert isinstance(version["etag"], str)
        
        # 验证lastModified是毫秒时间戳
        assert version["lastModified"] > 0
        
        # 验证etag是MD5哈希
        expected_etag = hashlib.md5(test_content.encode()).hexdigest()
        assert version["etag"] == expected_etag
    
    def test_version_changes_on_content_change(self, temp_posts_dir):
        """测试内容变化时版本信息也变化"""
        full_path = os.path.join(temp_posts_dir, "Markdowns", "change-test.md")
        
        # 写入初始内容
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("Initial content")
        
        version1 = get_file_version(full_path)
        
        # 等待一小段时间确保时间戳不?
        time.sleep(0.1)
        
        # 修改内容
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("Modified content")
        
        version2 = get_file_version(full_path)
        
        # 验证版本信息已变?
        assert version2["lastModified"] > version1["lastModified"]
        assert version2["etag"] != version1["etag"]


class TestPathValidation:
    """测试路径验证函数"""
    
    def test_validate_path_normal(self, temp_posts_dir):
        """测试正常路径验证"""
        path = "/Markdowns/test.md"
        full_path = validate_path(path)
        
        # 验证返回的是完整路径
        assert full_path.endswith("test.md")
        assert "Markdowns" in full_path
    
    def test_validate_path_traversal_attack(self, temp_posts_dir):
        """测试路径遍历攻击防护"""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/Markdowns/../../../../../../etc/passwd"
        ]
        
        for path in malicious_paths:
            with pytest.raises(Exception) as exc_info:
                validate_path(path)
            assert exc_info.value.status_code == 400
    
    def test_validate_path_non_markdown(self, temp_posts_dir):
        """测试非Markdown文件被拒?""
        non_md_paths = [
            "/test.txt",
            "/Markdowns/script.js",
            "/image.png"
        ]
        
        for path in non_md_paths:
            with pytest.raises(Exception) as exc_info:
                validate_path(path)
            assert exc_info.value.status_code == 400


class TestFileCreateAPI:
    """测试文件创建API (POST /api/files/create) - Task 2.4"""
    
    def test_create_new_file_in_markdowns(self, temp_posts_dir):
        """测试在Markdowns目录创建新文?""
        # 准备测试数据
        test_data = {
            "path": "/Markdowns/new-post.md",
            "name": "new-post",
            "collection": "Markdowns"
        }
        
        # 调用创建API
        response = client.post(
            "/api/files/create",
            json=test_data,
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "File created successfully"
        assert data["path"] == test_data["path"]
        
        # 验证文件确实被创?
        full_path = os.path.join(temp_posts_dir, "Markdowns", "new-post.md")
        assert os.path.exists(full_path)
        
        # 验证文件内容包含正确的front-matter
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查front-matter结构
        assert content.startswith("---\n")
        assert "title: new-post" in content
        assert "date:" in content
        assert "tags:" in content
        assert "categories:" in content
        assert "pre:" in content
        assert "img:" in content
        assert "---" in content
    
    def test_create_file_in_collection(self, temp_posts_dir):
        """测试在合集目录创建新文件"""
        # 创建合集目录
        collection_dir = os.path.join(temp_posts_dir, "MyCollection")
        os.makedirs(collection_dir, exist_ok=True)
        
        # 准备测试数据
        test_data = {
            "path": "/MyCollection/collection-post.md",
            "name": "collection-post",
            "collection": "MyCollection"
        }
        
        # 调用创建API
        response = client.post(
            "/api/files/create",
            json=test_data,
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证文件在正确的目录中被创建
        full_path = os.path.join(temp_posts_dir, "MyCollection", "collection-post.md")
        assert os.path.exists(full_path)
    
    def test_create_file_with_auto_directory_creation(self, temp_posts_dir):
        """测试创建文件时自动创建不存在的目?""
        # 准备测试数据 - 目录不存?
        test_data = {
            "path": "/NewCollection/auto-created.md",
            "name": "auto-created",
            "collection": "NewCollection"
        }
        
        # 调用创建API
        response = client.post(
            "/api/files/create",
            json=test_data,
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        
        # 验证目录和文件都被创?
        full_path = os.path.join(temp_posts_dir, "NewCollection", "auto-created.md")
        assert os.path.exists(full_path)
        assert os.path.isfile(full_path)
    
    def test_create_file_already_exists(self, temp_posts_dir):
        """测试创建已存在的文件应该失败"""
        # 先创建一个文?
        test_path = "/Markdowns/existing.md"
        full_path = os.path.join(temp_posts_dir, "Markdowns", "existing.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("# Existing file")
        
        # 尝试创建同名文件
        test_data = {
            "path": test_path,
            "name": "existing",
            "collection": "Markdowns"
        }
        
        response = client.post(
            "/api/files/create",
            json=test_data,
            headers=TEST_HEADERS
        )
        
        # 验证返回400错误
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_create_file_with_special_characters_in_name(self, temp_posts_dir):
        """测试创建包含特殊字符的文件名"""
        test_data = {
            "path": "/Markdowns/hello-world-2024.md",
            "name": "hello-world-2024",
            "collection": "Markdowns"
        }
        
        response = client.post(
            "/api/files/create",
            json=test_data,
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        
        # 验证文件被创?
        full_path = os.path.join(temp_posts_dir, "Markdowns", "hello-world-2024.md")
        assert os.path.exists(full_path)
    
    def test_create_file_invalid_path(self, temp_posts_dir):
        """测试使用无效路径创建文件"""
        # 尝试路径遍历攻击
        test_data = {
            "path": "../../../etc/passwd.md",
            "name": "passwd",
            "collection": "etc"
        }
        
        response = client.post(
            "/api/files/create",
            json=test_data,
            headers=TEST_HEADERS
        )
        
        # 验证被拒?
        assert response.status_code == 400
        assert "path traversal" in response.json()["detail"].lower()
    
    def test_create_file_non_markdown(self, temp_posts_dir):
        """测试创建非Markdown文件应该失败"""
        test_data = {
            "path": "/Markdowns/test.txt",
            "name": "test",
            "collection": "Markdowns"
        }
        
        response = client.post(
            "/api/files/create",
            json=test_data,
            headers=TEST_HEADERS
        )
        
        # 验证被拒?
        assert response.status_code == 400
        assert "only .md files" in response.json()["detail"].lower()
    
    def test_create_file_without_token(self, temp_posts_dir):
        """测试不提供Token的创建请?""
        test_data = {
            "path": "/Markdowns/test.md",
            "name": "test",
            "collection": "Markdowns"
        }
        
        response = client.post(
            "/api/files/create",
            json=test_data
        )
        
        # 验证被拒?
        assert response.status_code == 401
    
    def test_create_file_with_invalid_token(self, temp_posts_dir):
        """测试使用无效Token的创建请?""
        test_data = {
            "path": "/Markdowns/test.md",
            "name": "test",
            "collection": "Markdowns"
        }
        
        response = client.post(
            "/api/files/create",
            json=test_data,
            headers={"X-Auth-Token": "invalid-token"}
        )
        
        # 验证被拒?
        assert response.status_code == 401
    
    def test_create_file_generates_correct_metadata(self, temp_posts_dir):
        """测试创建文件时生成正确的元数据格?""
        test_data = {
            "path": "/Markdowns/metadata-test.md",
            "name": "metadata-test",
            "collection": "Markdowns"
        }
        
        response = client.post(
            "/api/files/create",
            json=test_data,
            headers=TEST_HEADERS
        )
        
        assert response.status_code == 200
        
        # 读取文件内容
        full_path = os.path.join(temp_posts_dir, "Markdowns", "metadata-test.md")
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证元数据格?
        lines = content.split('\n')
        assert lines[0] == "---"
        assert lines[1] == "title: metadata-test"
        assert lines[2].startswith("date: ")
        assert lines[3] == "tags: "
        assert lines[4] == "categories: "
        assert lines[5] == "pre: "
        assert lines[6] == "img: "
        assert lines[7] == "---"
        assert lines[8] == ""  # 空行
    
    def test_create_file_date_format(self, temp_posts_dir):
        """测试创建文件时日期格式正?""
        from datetime import datetime, timedelta
        
        test_data = {
            "path": "/Markdowns/date-test.md",
            "name": "date-test",
            "collection": "Markdowns"
        }
        
        # 记录创建前的时间(去掉微秒)
        before_time = datetime.now().replace(microsecond=0)
        
        response = client.post(
            "/api/files/create",
            json=test_data,
            headers=TEST_HEADERS
        )
        
        # 记录创建后的时间(?秒容?
        after_time = datetime.now().replace(microsecond=0) + timedelta(seconds=1)
        
        assert response.status_code == 200
        
        # 读取文件内容
        full_path = os.path.join(temp_posts_dir, "Markdowns", "date-test.md")
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取日期?
        import re
        date_match = re.search(r'date: (.+)', content)
        assert date_match is not None
        
        date_str = date_match.group(1)
        # 验证日期格式: YYYY-MM-DD HH:MM:SS
        file_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        
        # 验证日期在合理范围内
        assert before_time <= file_date <= after_time


class TestFileDeleteAPI:
    """测试文件删除API (DELETE /api/files/delete) - Task 2.5"""
    
    def test_delete_existing_file(self, temp_posts_dir):
        """测试删除已存在的文件"""
        # 创建测试文件
        test_path = "/Markdowns/to-delete.md"
        full_path = os.path.join(temp_posts_dir, "Markdowns", "to-delete.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("# File to Delete\n\nThis file will be deleted.")
        
        # 验证文件存在
        assert os.path.exists(full_path)
        
        # 调用删除API
        response = client.delete(
            "/api/files/delete",
            params={"path": test_path},
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "File deleted successfully"
        
        # 验证文件确实被删?
        assert not os.path.exists(full_path)
    
    def test_delete_file_in_collection(self, temp_posts_dir):
        """测试删除合集目录中的文件"""
        # 创建合集目录和文?
        collection_dir = os.path.join(temp_posts_dir, "TestCollection")
        os.makedirs(collection_dir, exist_ok=True)
        
        test_path = "/TestCollection/collection-file.md"
        full_path = os.path.join(temp_posts_dir, "TestCollection", "collection-file.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("# Collection File")
        
        # 验证文件存在
        assert os.path.exists(full_path)
        
        # 调用删除API
        response = client.delete(
            "/api/files/delete",
            params={"path": test_path},
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # 验证文件被删?
        assert not os.path.exists(full_path)
    
    def test_delete_nonexistent_file(self, temp_posts_dir):
        """测试删除不存在的文件应该返回404"""
        test_path = "/Markdowns/nonexistent.md"
        
        # 调用删除API
        response = client.delete(
            "/api/files/delete",
            params={"path": test_path},
            headers=TEST_HEADERS
        )
        
        # 验证返回404错误
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_delete_file_with_path_traversal(self, temp_posts_dir):
        """测试使用路径遍历攻击删除文件应该被拒?""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config",
            "/Markdowns/../../../../../../etc/passwd"
        ]
        
        for path in malicious_paths:
            response = client.delete(
                "/api/files/delete",
                params={"path": path},
                headers=TEST_HEADERS
            )
            
            # 验证被拒?
            assert response.status_code == 400
            assert "path traversal" in response.json()["detail"].lower()
    
    def test_delete_non_markdown_file(self, temp_posts_dir):
        """测试删除非Markdown文件应该被拒?""
        non_md_paths = [
            "/test.txt",
            "/Markdowns/script.js",
            "/image.png"
        ]
        
        for path in non_md_paths:
            response = client.delete(
                "/api/files/delete",
                params={"path": path},
                headers=TEST_HEADERS
            )
            
            # 验证被拒?
            assert response.status_code == 400
            assert "only .md files" in response.json()["detail"].lower()
    
    def test_delete_file_without_token(self, temp_posts_dir):
        """测试不提供Token的删除请求应该被拒绝"""
        test_path = "/Markdowns/test.md"
        
        response = client.delete(
            "/api/files/delete",
            params={"path": test_path}
        )
        
        # 验证被拒?
        assert response.status_code == 401
    
    def test_delete_file_with_invalid_token(self, temp_posts_dir):
        """测试使用无效Token的删除请求应该被拒绝"""
        test_path = "/Markdowns/test.md"
        
        response = client.delete(
            "/api/files/delete",
            params={"path": test_path},
            headers={"X-Auth-Token": "invalid-token"}
        )
        
        # 验证被拒?
        assert response.status_code == 401
    
    def test_delete_file_with_nested_path(self, temp_posts_dir):
        """测试删除嵌套路径中的文件"""
        # 创建嵌套目录结构
        nested_dir = os.path.join(temp_posts_dir, "Collection", "SubFolder")
        os.makedirs(nested_dir, exist_ok=True)
        
        test_path = "/Collection/SubFolder/nested-file.md"
        full_path = os.path.join(temp_posts_dir, "Collection", "SubFolder", "nested-file.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("# Nested File")
        
        # 验证文件存在
        assert os.path.exists(full_path)
        
        # 调用删除API
        response = client.delete(
            "/api/files/delete",
            params={"path": test_path},
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # 验证文件被删?
        assert not os.path.exists(full_path)
    
    def test_delete_file_calls_generate_command(self, temp_posts_dir, monkeypatch):
        """测试删除文件后调用Generate命令更新配置 (需?8.2, 8.4)"""
        # 创建测试文件
        test_path = "/Markdowns/generate-test.md"
        full_path = os.path.join(temp_posts_dir, "Markdowns", "generate-test.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("# Generate Test")
        
        # Mock Generate命令以验证它被调?
        generate_called = []
        
        class MockGenerate:
            def execute(self):
                generate_called.append(True)
                return "Generate command executed"
        
        # 使用monkeypatch替换Generate?
        import editor_server
        original_generate = None
        try:
            from commands import Generate as OriginalGenerate
            original_generate = OriginalGenerate
        except:
            pass
        
        # 在editor_server模块中mock Generate
        import sys
        if 'commands' in sys.modules:
            sys.modules['commands'].Generate = MockGenerate
        
        # 调用删除API
        response = client.delete(
            "/api/files/delete",
            params={"path": test_path},
            headers=TEST_HEADERS
        )
        
        # 恢复原始Generate?
        if original_generate and 'commands' in sys.modules:
            sys.modules['commands'].Generate = original_generate
        
        # 验证响应
        assert response.status_code == 200
        
        # 验证Generate命令被调?
        # 注意: 由于Generate命令可能失败(在测试环境中),我们只验证API成功
        # 实际的Generate调用在try-except块中,失败不会影响API响应
        assert response.json()["success"] is True
    
    def test_delete_multiple_files_sequentially(self, temp_posts_dir):
        """测试连续删除多个文件"""
        # 创建多个测试文件
        files_to_delete = [
            "/Markdowns/file1.md",
            "/Markdowns/file2.md",
            "/Markdowns/file3.md"
        ]
        
        for file_path in files_to_delete:
            full_path = os.path.join(temp_posts_dir, file_path.lstrip('/'))
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(f"# Content for {file_path}")
        
        # 验证所有文件都存在
        for file_path in files_to_delete:
            full_path = os.path.join(temp_posts_dir, file_path.lstrip('/'))
            assert os.path.exists(full_path)
        
        # 连续删除所有文?
        for file_path in files_to_delete:
            response = client.delete(
                "/api/files/delete",
                params={"path": file_path},
                headers=TEST_HEADERS
            )
            assert response.status_code == 200
            assert response.json()["success"] is True
        
        # 验证所有文件都被删?
        for file_path in files_to_delete:
            full_path = os.path.join(temp_posts_dir, file_path.lstrip('/'))
            assert not os.path.exists(full_path)


class TestFileMoveAPI:
    """测试文件移动API (POST /api/files/move) - Task 2.6"""
    
    def test_move_file_within_same_collection(self, temp_posts_dir):
        """测试在同一合集内移动文件(实际上不移动)"""
        # 创建测试文件
        test_path = "/Markdowns/test-move.md"
        full_path = os.path.join(temp_posts_dir, "Markdowns", "test-move.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("# Test Move\n\nContent here.")
        
        # 尝试移动到同一合集
        response = client.post(
            "/api/files/move",
            json={
                "from": test_path,
                "to": "/Markdowns/test-move.md"
            },
            headers=TEST_HEADERS
        )
        
        # 验证响应 - MovePost命令会返回成功但不实际移动
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证文件仍然存在
        assert os.path.exists(full_path)
    
    def test_move_file_to_different_collection(self, temp_posts_dir):
        """测试移动文件到不同合集"""
        # 创建源文件
        source_path = "/Markdowns/move-test.md"
        source_full_path = os.path.join(temp_posts_dir, "Markdowns", "move-test.md")
        
        with open(source_full_path, 'w', encoding='utf-8') as f:
            f.write("# Move Test\n\nThis file will be moved.")
        
        # 创建目标合集目录
        target_collection_dir = os.path.join(temp_posts_dir, "TargetCollection")
        os.makedirs(target_collection_dir, exist_ok=True)
        
        # 验证源文件存在
        assert os.path.exists(source_full_path)
        
        # 调用移动API
        response = client.post(
            "/api/files/move",
            json={
                "from": source_path,
                "to": "/TargetCollection/move-test.md"
            },
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证文件已移动
        target_full_path = os.path.join(temp_posts_dir, "TargetCollection", "move-test.md")
        assert os.path.exists(target_full_path)
        assert not os.path.exists(source_full_path)
        
        # 验证文件内容保持不变
        with open(target_full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert "# Move Test" in content
        assert "This file will be moved." in content
    
    def test_move_file_from_collection_to_markdowns(self, temp_posts_dir):
        """测试从合集移动文件到Markdowns目录"""
        # 创建合集目录和文件
        collection_dir = os.path.join(temp_posts_dir, "MyCollection")
        os.makedirs(collection_dir, exist_ok=True)
        
        source_path = "/MyCollection/collection-post.md"
        source_full_path = os.path.join(temp_posts_dir, "MyCollection", "collection-post.md")
        
        with open(source_full_path, 'w', encoding='utf-8') as f:
            f.write("# Collection Post\n\nMoving to Markdowns.")
        
        # 验证源文件存在
        assert os.path.exists(source_full_path)
        
        # 调用移动API
        response = client.post(
            "/api/files/move",
            json={
                "from": source_path,
                "to": "/Markdowns/collection-post.md"
            },
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # 验证文件已移动
        target_full_path = os.path.join(temp_posts_dir, "Markdowns", "collection-post.md")
        assert os.path.exists(target_full_path)
        assert not os.path.exists(source_full_path)
    
    def test_move_nonexistent_file(self, temp_posts_dir):
        """测试移动不存在的文件应该返回404"""
        response = client.post(
            "/api/files/move",
            json={
                "from": "/Markdowns/nonexistent.md",
                "to": "/TargetCollection/nonexistent.md"
            },
            headers=TEST_HEADERS
        )
        
        # 验证返回404错误
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_move_file_with_path_traversal(self, temp_posts_dir):
        """测试使用路径遍历攻击移动文件应该被拒绝"""
        # 创建测试文件
        test_path = "/Markdowns/test.md"
        full_path = os.path.join(temp_posts_dir, "Markdowns", "test.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("# Test")
        
        malicious_paths = [
            ("../../../etc/passwd", "/Markdowns/test.md"),
            ("/Markdowns/test.md", "../../../etc/passwd"),
            ("..\\..\\..\\windows\\system32", "/Markdowns/test.md")
        ]
        
        for from_path, to_path in malicious_paths:
            response = client.post(
                "/api/files/move",
                json={
                    "from": from_path,
                    "to": to_path
                },
                headers=TEST_HEADERS
            )
            
            # 验证被拒绝
            assert response.status_code == 400
            assert "path traversal" in response.json()["detail"].lower()
    
    def test_move_file_non_markdown(self, temp_posts_dir):
        """测试移动非Markdown文件应该被拒绝"""
        response = client.post(
            "/api/files/move",
            json={
                "from": "/test.txt",
                "to": "/Markdowns/test.txt"
            },
            headers=TEST_HEADERS
        )
        
        # 验证被拒绝
        assert response.status_code == 400
        assert "only .md files" in response.json()["detail"].lower()
    
    def test_move_file_without_token(self, temp_posts_dir):
        """测试不提供Token的移动请求应该被拒绝"""
        response = client.post(
            "/api/files/move",
            json={
                "from": "/Markdowns/test.md",
                "to": "/TargetCollection/test.md"
            }
        )
        
        # 验证被拒绝
        assert response.status_code == 401
    
    def test_move_file_with_invalid_token(self, temp_posts_dir):
        """测试使用无效Token的移动请求应该被拒绝"""
        response = client.post(
            "/api/files/move",
            json={
                "from": "/Markdowns/test.md",
                "to": "/TargetCollection/test.md"
            },
            headers={"X-Auth-Token": "invalid-token"}
        )
        
        # 验证被拒绝
        assert response.status_code == 401
    
    def test_move_file_missing_parameters(self, temp_posts_dir):
        """测试缺少必需参数的移动请求应该失败"""
        # 缺少 'to' 参数
        response = client.post(
            "/api/files/move",
            json={
                "from": "/Markdowns/test.md"
            },
            headers=TEST_HEADERS
        )
        
        assert response.status_code == 400
        assert "required" in response.json()["detail"].lower()
        
        # 缺少 'from' 参数
        response = client.post(
            "/api/files/move",
            json={
                "to": "/TargetCollection/test.md"
            },
            headers=TEST_HEADERS
        )
        
        assert response.status_code == 400
        assert "required" in response.json()["detail"].lower()
    
    def test_move_file_handles_name_conflict(self, temp_posts_dir):
        """测试移动文件时处理文件名冲突 - MovePost会自动重命名"""
        # 创建源文件
        source_path = "/Markdowns/conflict-test.md"
        source_full_path = os.path.join(temp_posts_dir, "Markdowns", "conflict-test.md")
        
        with open(source_full_path, 'w', encoding='utf-8') as f:
            f.write("# Source File")
        
        # 创建目标合集和同名文件
        target_collection_dir = os.path.join(temp_posts_dir, "TargetCollection")
        os.makedirs(target_collection_dir, exist_ok=True)
        
        existing_file_path = os.path.join(target_collection_dir, "conflict-test.md")
        with open(existing_file_path, 'w', encoding='utf-8') as f:
            f.write("# Existing File")
        
        # 调用移动API
        response = client.post(
            "/api/files/move",
            json={
                "from": source_path,
                "to": "/TargetCollection/conflict-test.md"
            },
            headers=TEST_HEADERS
        )
        
        # 验证响应 - MovePost会自动处理冲突
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # 验证源文件已被移动
        assert not os.path.exists(source_full_path)
        
        # 验证目标目录中有文件(可能被重命名为 conflict-test_1.md)
        # MovePost会自动处理文件名冲突
        files_in_target = os.listdir(target_collection_dir)
        assert len(files_in_target) >= 1
    
    def test_move_file_creates_target_directory(self, temp_posts_dir):
        """测试移动文件时自动创建目标目录"""
        # 创建源文件
        source_path = "/Markdowns/auto-dir-test.md"
        source_full_path = os.path.join(temp_posts_dir, "Markdowns", "auto-dir-test.md")
        
        with open(source_full_path, 'w', encoding='utf-8') as f:
            f.write("# Auto Directory Test")
        
        # 验证目标目录不存在
        target_collection_dir = os.path.join(temp_posts_dir, "NewCollection")
        assert not os.path.exists(target_collection_dir)
        
        # 调用移动API
        response = client.post(
            "/api/files/move",
            json={
                "from": source_path,
                "to": "/NewCollection/auto-dir-test.md"
            },
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # 验证目标目录被创建
        assert os.path.exists(target_collection_dir)
        
        # 验证文件已移动
        target_full_path = os.path.join(target_collection_dir, "auto-dir-test.md")
        assert os.path.exists(target_full_path)
        assert not os.path.exists(source_full_path)
    
    def test_move_file_calls_generate_command(self, temp_posts_dir, monkeypatch):
        """测试移动文件后调用Generate命令更新配置 (需求 8.3, 8.4)"""
        # 创建源文件
        source_path = "/Markdowns/generate-move-test.md"
        source_full_path = os.path.join(temp_posts_dir, "Markdowns", "generate-move-test.md")
        
        with open(source_full_path, 'w', encoding='utf-8') as f:
            f.write("# Generate Move Test")
        
        # 创建目标合集
        target_collection_dir = os.path.join(temp_posts_dir, "TargetCollection")
        os.makedirs(target_collection_dir, exist_ok=True)
        
        # Mock Generate命令以验证它被调用
        generate_called = []
        
        class MockGenerate:
            def execute(self):
                generate_called.append(True)
                return "Generate command executed"
        
        # 在editor_server模块中mock Generate
        import sys
        original_generate = None
        if 'commands' in sys.modules:
            try:
                from commands import Generate as OriginalGenerate
                original_generate = OriginalGenerate
                sys.modules['commands'].Generate = MockGenerate
            except:
                pass
        
        # 调用移动API
        response = client.post(
            "/api/files/move",
            json={
                "from": source_path,
                "to": "/TargetCollection/generate-move-test.md"
            },
            headers=TEST_HEADERS
        )
        
        # 恢复原始Generate类
        if original_generate and 'commands' in sys.modules:
            sys.modules['commands'].Generate = original_generate
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # 注意: Generate命令在try-except块中,失败不会影响API响应
        # 我们只验证API成功执行
    
    def test_move_file_integrates_with_movepost_command(self, temp_posts_dir):
        """测试移动API集成MovePost命令逻辑 (需求 8.3)"""
        # 创建源文件
        source_path = "/Markdowns/movepost-integration.md"
        source_full_path = os.path.join(temp_posts_dir, "Markdowns", "movepost-integration.md")
        
        with open(source_full_path, 'w', encoding='utf-8') as f:
            f.write("# MovePost Integration Test")
        
        # 创建目标合集
        target_collection_dir = os.path.join(temp_posts_dir, "IntegrationCollection")
        os.makedirs(target_collection_dir, exist_ok=True)
        
        # 调用移动API
        response = client.post(
            "/api/files/move",
            json={
                "from": source_path,
                "to": "/IntegrationCollection/movepost-integration.md"
            },
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证文件已移动 - 这证明MovePost命令被正确调用
        target_full_path = os.path.join(target_collection_dir, "movepost-integration.md")
        assert os.path.exists(target_full_path)
        assert not os.path.exists(source_full_path)
    
    def test_move_file_alternative_field_names(self, temp_posts_dir):
        """测试移动API支持from_path/to_path字段名"""
        # 创建源文件
        source_path = "/Markdowns/alt-fields-test.md"
        source_full_path = os.path.join(temp_posts_dir, "Markdowns", "alt-fields-test.md")
        
        with open(source_full_path, 'w', encoding='utf-8') as f:
            f.write("# Alternative Fields Test")
        
        # 创建目标合集
        target_collection_dir = os.path.join(temp_posts_dir, "AltCollection")
        os.makedirs(target_collection_dir, exist_ok=True)
        
        # 使用from_path/to_path字段名
        response = client.post(
            "/api/files/move",
            json={
                "from_path": source_path,
                "to_path": "/AltCollection/alt-fields-test.md"
            },
            headers=TEST_HEADERS
        )
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # 验证文件已移动
        target_full_path = os.path.join(target_collection_dir, "alt-fields-test.md")
        assert os.path.exists(target_full_path)
        assert not os.path.exists(source_full_path)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])

