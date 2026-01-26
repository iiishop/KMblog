"""
Simple test for file move API - Task 2.6
"""

import os
import sys
import tempfile
import shutil

# Add mainTools to path
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from fastapi.testclient import TestClient
from editor_server import app

# Set test token
os.environ['AUTH_TOKEN'] = 'test-token-12345'
import editor_server
editor_server.AUTH_TOKEN = 'test-token-12345'

# Create test client
client = TestClient(app)

# Test headers
TEST_HEADERS = {"X-Auth-Token": "test-token-12345"}


@pytest.fixture
def temp_posts_dir(monkeypatch):
    """Create temporary Posts directory for testing"""
    temp_dir = tempfile.mkdtemp()
    posts_dir = os.path.join(temp_dir, "Posts", "Markdowns")
    os.makedirs(posts_dir, exist_ok=True)
    
    # Use monkeypatch to replace get_posts_path
    def mock_get_posts_path():
        return os.path.join(temp_dir, "Posts")
    
    # Replace function in editor_server module
    monkeypatch.setattr(editor_server, 'get_posts_path', mock_get_posts_path)
    
    # Also replace in path_utils module
    import path_utils
    monkeypatch.setattr(path_utils, 'get_posts_path', mock_get_posts_path)
    
    yield os.path.join(temp_dir, "Posts")
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestFileMoveAPI:
    """Test file move API (POST /api/files/move) - Task 2.6"""
    
    def test_move_file_to_different_collection(self, temp_posts_dir):
        """Test moving file to different collection"""
        # Create source file
        source_path = "/Markdowns/move-test.md"
        source_full_path = os.path.join(temp_posts_dir, "Markdowns", "move-test.md")
        
        with open(source_full_path, 'w', encoding='utf-8') as f:
            f.write("# Move Test\n\nThis file will be moved.")
        
        # Create target collection directory
        target_collection_dir = os.path.join(temp_posts_dir, "TargetCollection")
        os.makedirs(target_collection_dir, exist_ok=True)
        
        # Verify source file exists
        assert os.path.exists(source_full_path)
        
        # Call move API
        response = client.post(
            "/api/files/move",
            json={
                "from": source_path,
                "to": "/TargetCollection/move-test.md"
            },
            headers=TEST_HEADERS
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify file has been moved
        target_full_path = os.path.join(temp_posts_dir, "TargetCollection", "move-test.md")
        assert os.path.exists(target_full_path)
        assert not os.path.exists(source_full_path)
        
        # Verify file content is preserved
        with open(target_full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert "# Move Test" in content
        assert "This file will be moved." in content
    
    def test_move_nonexistent_file(self, temp_posts_dir):
        """Test moving nonexistent file should return 404"""
        response = client.post(
            "/api/files/move",
            json={
                "from": "/Markdowns/nonexistent.md",
                "to": "/TargetCollection/nonexistent.md"
            },
            headers=TEST_HEADERS
        )
        
        # Verify 404 error
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_move_file_with_path_traversal(self, temp_posts_dir):
        """Test path traversal attack should be rejected"""
        # Create test file
        test_path = "/Markdowns/test.md"
        full_path = os.path.join(temp_posts_dir, "Markdowns", "test.md")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("# Test")
        
        # Try path traversal
        response = client.post(
            "/api/files/move",
            json={
                "from": test_path,
                "to": "../../../etc/passwd"
            },
            headers=TEST_HEADERS
        )
        
        # Verify rejection
        assert response.status_code == 400
        assert "path traversal" in response.json()["detail"].lower()
    
    def test_move_file_without_token(self, temp_posts_dir):
        """Test move request without token should be rejected"""
        response = client.post(
            "/api/files/move",
            json={
                "from": "/Markdowns/test.md",
                "to": "/TargetCollection/test.md"
            }
        )
        
        # Verify rejection
        assert response.status_code == 401
    
    def test_move_file_creates_target_directory(self, temp_posts_dir):
        """Test moving file automatically creates target directory"""
        # Create source file
        source_path = "/Markdowns/auto-dir-test.md"
        source_full_path = os.path.join(temp_posts_dir, "Markdowns", "auto-dir-test.md")
        
        with open(source_full_path, 'w', encoding='utf-8') as f:
            f.write("# Auto Directory Test")
        
        # Verify target directory doesn't exist
        target_collection_dir = os.path.join(temp_posts_dir, "NewCollection")
        assert not os.path.exists(target_collection_dir)
        
        # Call move API
        response = client.post(
            "/api/files/move",
            json={
                "from": source_path,
                "to": "/NewCollection/auto-dir-test.md"
            },
            headers=TEST_HEADERS
        )
        
        # Debug: print response if failed
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
        
        # Verify response
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify target directory was created
        assert os.path.exists(target_collection_dir)
        
        # Verify file has been moved
        target_full_path = os.path.join(target_collection_dir, "auto-dir-test.md")
        assert os.path.exists(target_full_path)
        assert not os.path.exists(source_full_path)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
