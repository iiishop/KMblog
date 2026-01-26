"""
Test for file reading API endpoint (GET /api/files/read)
Tests requirement 1.1: FastAPI_Server SHALL 提供读取文件内容的API端点

Task 2.2: 实现文件读取API
- 验证文件路径
- 读取文件内容
- 解析front-matter元数据
- 返回文件版本信息(lastModified, etag)
"""
import sys
import os
import tempfile
import time

# Add mainTools to path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from editor_server import app
import editor_server

# Create test client
client = TestClient(app)


def test_read_existing_file():
    """Test reading an existing markdown file"""
    print("\n" + "="*60)
    print("Test 1: Reading an existing file")
    print("="*60)
    
    # Use a known existing file (path relative to Posts directory)
    test_path = "/Markdowns/纪念白求恩.md"
    
    response = client.get(
        "/api/files/read",
        params={"path": test_path},
        headers={"X-Auth-Token": editor_server.AUTH_TOKEN}
    )
    
    # Check status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("✓ Status code: 200")
    
    # Parse response
    data = response.json()
    
    # Verify response structure
    assert "content" in data, "Response should contain 'content' key"
    assert "version" in data, "Response should contain 'version' key"
    print("✓ Response has correct structure (content, version)")
    
    # Verify content is not empty
    content = data["content"]
    assert len(content) > 0, "Content should not be empty"
    print(f"✓ Content loaded ({len(content)} characters)")
    
    # Verify front-matter is present
    assert content.startswith("---"), "Content should start with front-matter delimiter"
    assert "title: 纪念白求恩" in content, "Content should contain title in front-matter"
    print("✓ Front-matter is present and contains expected data")
    
    # Verify version information
    version = data["version"]
    assert "lastModified" in version, "Version should contain 'lastModified'"
    assert "etag" in version, "Version should contain 'etag'"
    print("✓ Version information present (lastModified, etag)")
    
    # Verify lastModified is a valid timestamp (milliseconds)
    last_modified = version["lastModified"]
    assert isinstance(last_modified, int), "lastModified should be an integer"
    assert last_modified > 0, "lastModified should be positive"
    # Check it's a reasonable timestamp (after 2020-01-01)
    assert last_modified > 1577836800000, "lastModified should be a valid timestamp"
    print(f"✓ lastModified is valid: {last_modified}")
    
    # Verify etag is a valid MD5 hash
    etag = version["etag"]
    assert isinstance(etag, str), "etag should be a string"
    assert len(etag) == 32, "etag should be 32 characters (MD5 hash)"
    assert all(c in "0123456789abcdef" for c in etag), "etag should be hexadecimal"
    print(f"✓ etag is valid MD5 hash: {etag[:8]}...")
    
    print("✅ Test 1 passed: Successfully read existing file with correct structure")
    return data


def test_read_nonexistent_file():
    """Test reading a file that doesn't exist"""
    print("\n" + "="*60)
    print("Test 2: Reading a non-existent file")
    print("="*60)
    
    test_path = "/Markdowns/this-file-does-not-exist.md"
    
    response = client.get(
        "/api/files/read",
        params={"path": test_path},
        headers={"X-Auth-Token": editor_server.AUTH_TOKEN}
    )
    
    # Should return 404
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    print("✓ Returns 404 for non-existent file")
    
    # Check error message
    data = response.json()
    assert "detail" in data, "Error response should contain 'detail'"
    assert "not found" in data["detail"].lower(), "Error message should mention 'not found'"
    print(f"✓ Error message: {data['detail']}")
    
    print("✅ Test 2 passed: Correctly handles non-existent files")


def test_path_traversal_protection():
    """Test that path traversal attacks are blocked"""
    print("\n" + "="*60)
    print("Test 3: Path traversal protection")
    print("="*60)
    
    # Test various path traversal attempts
    malicious_paths = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "/Markdowns/../../../../../../etc/passwd",
        "Markdowns/../../../etc/passwd",
    ]
    
    for path in malicious_paths:
        response = client.get(
            "/api/files/read",
            params={"path": path},
            headers={"X-Auth-Token": editor_server.AUTH_TOKEN}
        )
        
        # Should return 400 (bad request)
        assert response.status_code == 400, \
            f"Path traversal should return 400, got {response.status_code} for {path}"
        
        data = response.json()
        assert "detail" in data, "Error response should contain 'detail'"
        detail_lower = data["detail"].lower()
        assert "invalid" in detail_lower or "path traversal" in detail_lower, \
            f"Error should mention invalid path or path traversal: {data['detail']}"
        
        print(f"✓ Blocked: {path}")
    
    print("✅ Test 3 passed: Path traversal attacks are properly blocked")


def test_non_markdown_file_rejection():
    """Test that non-.md files are rejected"""
    print("\n" + "="*60)
    print("Test 4: Non-markdown file rejection")
    print("="*60)
    
    # Test various non-.md file extensions
    invalid_paths = [
        "/test.txt",
        "/test.html",
        "/test.js",
        "/test",  # No extension
        "/XJTLU/image.png",  # Actual non-md file in the directory
    ]
    
    for path in invalid_paths:
        response = client.get(
            "/api/files/read",
            params={"path": path},
            headers={"X-Auth-Token": editor_server.AUTH_TOKEN}
        )
        
        # Should return 400 (bad request)
        assert response.status_code == 400, \
            f"Non-.md file should return 400, got {response.status_code} for {path}"
        
        data = response.json()
        assert "detail" in data, "Error response should contain 'detail'"
        assert "only .md files" in data["detail"].lower() or "invalid file type" in data["detail"].lower(), \
            f"Error should mention .md files only: {data['detail']}"
        
        print(f"✓ Rejected: {path}")
    
    print("✅ Test 4 passed: Non-markdown files are properly rejected")


def test_authentication_required():
    """Test that authentication is required"""
    print("\n" + "="*60)
    print("Test 5: Authentication requirement")
    print("="*60)
    
    test_path = "/Markdowns/纪念白求恩.md"
    
    # Test without token
    response = client.get(
        "/api/files/read",
        params={"path": test_path}
    )
    assert response.status_code == 401, "Should return 401 without token"
    print("✓ Returns 401 without authentication token")
    
    # Test with invalid token
    response = client.get(
        "/api/files/read",
        params={"path": test_path},
        headers={"X-Auth-Token": "invalid-token-12345"}
    )
    assert response.status_code == 401, "Should return 401 with invalid token"
    print("✓ Returns 401 with invalid token")
    
    print("✅ Test 5 passed: Authentication is properly enforced")


def test_version_consistency():
    """Test that version information is consistent across multiple reads"""
    print("\n" + "="*60)
    print("Test 6: Version consistency")
    print("="*60)
    
    test_path = "/Markdowns/纪念白求恩.md"
    
    # Read the file twice
    response1 = client.get(
        "/api/files/read",
        params={"path": test_path},
        headers={"X-Auth-Token": editor_server.AUTH_TOKEN}
    )
    
    time.sleep(0.1)  # Small delay
    
    response2 = client.get(
        "/api/files/read",
        params={"path": test_path},
        headers={"X-Auth-Token": editor_server.AUTH_TOKEN}
    )
    
    data1 = response1.json()
    data2 = response2.json()
    
    # Version should be identical if file hasn't changed
    assert data1["version"]["lastModified"] == data2["version"]["lastModified"], \
        "lastModified should be consistent"
    assert data1["version"]["etag"] == data2["version"]["etag"], \
        "etag should be consistent"
    print("✓ Version information is consistent across multiple reads")
    
    # Content should be identical
    assert data1["content"] == data2["content"], "Content should be identical"
    print("✓ Content is identical across multiple reads")
    
    print("✅ Test 6 passed: Version information is consistent")


def test_different_files_different_versions():
    """Test that different files have different version information"""
    print("\n" + "="*60)
    print("Test 7: Different files have different versions")
    print("="*60)
    
    # Read two different files
    file1 = "/Markdowns/纪念白求恩.md"
    file2 = "/Markdowns/hello-world.md"
    
    response1 = client.get(
        "/api/files/read",
        params={"path": file1},
        headers={"X-Auth-Token": editor_server.AUTH_TOKEN}
    )
    
    response2 = client.get(
        "/api/files/read",
        params={"path": file2},
        headers={"X-Auth-Token": editor_server.AUTH_TOKEN}
    )
    
    data1 = response1.json()
    data2 = response2.json()
    
    # ETags should be different (different content)
    assert data1["version"]["etag"] != data2["version"]["etag"], \
        "Different files should have different etags"
    print("✓ Different files have different etags")
    
    # Content should be different
    assert data1["content"] != data2["content"], \
        "Different files should have different content"
    print("✓ Different files have different content")
    
    print("✅ Test 7 passed: Different files have different versions")


def test_utf8_encoding():
    """Test that UTF-8 encoding is handled correctly"""
    print("\n" + "="*60)
    print("Test 8: UTF-8 encoding support")
    print("="*60)
    
    # Read a file with Chinese characters
    test_path = "/Markdowns/纪念白求恩.md"
    
    response = client.get(
        "/api/files/read",
        params={"path": test_path},
        headers={"X-Auth-Token": editor_server.AUTH_TOKEN}
    )
    
    data = response.json()
    content = data["content"]
    
    # Verify Chinese characters are present and correctly encoded
    assert "白求恩" in content, "Chinese characters should be present"
    assert "共产党" in content, "Chinese characters should be correctly encoded"
    assert "国际主义" in content, "Chinese characters should be readable"
    print("✓ Chinese characters are correctly encoded")
    
    # Verify special characters
    assert "——" in content or "—" in content or "-" in content, "Special characters should be present"
    print("✓ Special characters are handled correctly")
    
    print("✅ Test 8 passed: UTF-8 encoding is properly supported")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("FILE READ API TEST SUITE")
    print("Testing: GET /api/files/read")
    print("Task 2.2: 实现文件读取API")
    print("="*60)
    
    # Set test token
    editor_server.AUTH_TOKEN = "test-token-12345"
    
    try:
        # Run all tests
        test_read_existing_file()
        test_read_nonexistent_file()
        test_path_traversal_protection()
        test_non_markdown_file_rejection()
        test_authentication_required()
        test_version_consistency()
        test_different_files_different_versions()
        test_utf8_encoding()
        
        # Summary
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nVerified functionality:")
        print("  ✓ File path validation")
        print("  ✓ File content reading")
        print("  ✓ Front-matter preservation")
        print("  ✓ Version information (lastModified, etag)")
        print("  ✓ Path traversal protection")
        print("  ✓ Non-.md file rejection")
        print("  ✓ Authentication enforcement")
        print("  ✓ Version consistency")
        print("  ✓ UTF-8 encoding support")
        print("\n✅ Task 2.2 implementation verified successfully!")
        print("="*60)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
