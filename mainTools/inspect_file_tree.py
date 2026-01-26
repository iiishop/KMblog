"""
Inspect the actual file tree structure returned by the API
"""
import sys
import os
import json

# Add mainTools to path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from editor_server import app
import editor_server

# Set test token
editor_server.AUTH_TOKEN = "test-token-12345"

# Create test client
client = TestClient(app)

# Get file tree
response = client.get(
    "/api/files/tree",
    headers={"X-Auth-Token": "test-token-12345"}
)

data = response.json()

# Pretty print the structure (limited depth for readability)
def print_tree(items, indent=0, max_depth=2):
    for item in items:
        prefix = "  " * indent
        if item["type"] == "folder":
            print(f"{prefix}📁 {item['name']} ({item['path']})")
            if indent < max_depth and "children" in item:
                print_tree(item["children"], indent + 1, max_depth)
                if indent < max_depth:
                    file_count = sum(1 for child in item["children"] if child["type"] == "file")
                    if file_count > 0:
                        print(f"{prefix}   └─ ({file_count} files)")
        else:
            print(f"{prefix}📄 {item['name']} ({item['path']})")

print("File Tree Structure:")
print("=" * 60)
print_tree(data["tree"])
print("=" * 60)

# Print JSON sample
print("\nJSON Structure Sample (first folder):")
print(json.dumps(data["tree"][0], indent=2))
