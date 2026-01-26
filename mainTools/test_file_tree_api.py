"""
Simple test to verify the file tree API endpoint works correctly
"""
import sys
import os

# Add mainTools to path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from editor_server import app, AUTH_TOKEN

# Create test client
client = TestClient(app)

def test_file_tree_endpoint():
    """Test that the file tree endpoint returns the correct structure"""
    print("Testing GET /api/files/tree endpoint...")
    
    # Make request with auth token
    response = client.get(
        "/api/files/tree",
        headers={"X-Auth-Token": AUTH_TOKEN}
    )
    
    # Check response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("✓ Status code: 200")
    
    # Parse response
    data = response.json()
    assert "tree" in data, "Response should contain 'tree' key"
    print("✓ Response contains 'tree' key")
    
    tree = data["tree"]
    assert isinstance(tree, list), "Tree should be a list"
    print(f"✓ Tree is a list with {len(tree)} top-level items")
    
    # Verify structure
    for item in tree:
        assert "name" in item, "Each item should have 'name'"
        assert "type" in item, "Each item should have 'type'"
        assert "path" in item, "Each item should have 'path'"
        assert item["type"] in ["file", "folder"], "Type should be 'file' or 'folder'"
        
        if item["type"] == "folder":
            assert "children" in item, "Folders should have 'children'"
            assert isinstance(item["children"], list), "Children should be a list"
    
    print("✓ All items have correct structure")
    
    # Verify specific folders exist
    folder_names = [item["name"] for item in tree if item["type"] == "folder"]
    print(f"✓ Found folders: {folder_names}")
    
    # Verify Images folder is NOT included
    assert "Images" not in folder_names, "Images folder should be excluded"
    print("✓ Images folder is correctly excluded")
    
    # Check that we have expected folders
    expected_folders = ["Code", "Markdowns", "XJTLU"]
    for folder in expected_folders:
        assert folder in folder_names, f"Expected folder '{folder}' not found"
    print(f"✓ All expected folders present: {expected_folders}")
    
    # Verify files are .md only
    def check_files_recursive(items):
        for item in items:
            if item["type"] == "file":
                assert item["name"].endswith(".md"), f"File {item['name']} should be .md"
            elif item["type"] == "folder" and "children" in item:
                check_files_recursive(item["children"])
    
    check_files_recursive(tree)
    print("✓ All files are .md files")
    
    # Verify paths are correct format
    def check_paths_recursive(items):
        for item in items:
            assert item["path"].startswith("/Posts/"), f"Path should start with /Posts/: {item['path']}"
            if item["type"] == "folder" and "children" in item:
                check_paths_recursive(item["children"])
    
    check_paths_recursive(tree)
    print("✓ All paths have correct format")
    
    print("\n✅ All tests passed! File tree API is working correctly.")
    return True


def test_file_tree_without_token():
    """Test that the endpoint requires authentication"""
    print("\nTesting authentication requirement...")
    
    response = client.get("/api/files/tree")
    assert response.status_code == 401, "Should return 401 without token"
    print("✓ Returns 401 without authentication token")
    
    response = client.get(
        "/api/files/tree",
        headers={"X-Auth-Token": "invalid-token"}
    )
    assert response.status_code == 401, "Should return 401 with invalid token"
    print("✓ Returns 401 with invalid token")
    
    print("✅ Authentication is working correctly.")
    return True


if __name__ == "__main__":
    # Set a test token
    import editor_server
    editor_server.AUTH_TOKEN = "test-token-12345"
    AUTH_TOKEN = "test-token-12345"
    
    try:
        test_file_tree_endpoint()
        test_file_tree_without_token()
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✅")
        print("="*60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
