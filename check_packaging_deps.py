"""
检查打包所需的依赖是否都已安装
"""

import sys

print("=" * 60)
print("检查打包依赖")
print("=" * 60)

required_packages = [
    ('flet', 'Flet GUI 框架'),
    ('fastapi', 'FastAPI Web 框架'),
    ('uvicorn', 'ASGI 服务器'),
    ('pydantic', '数据验证'),
    ('starlette', 'ASGI 工具包'),
    ('requests', 'HTTP 客户端'),
    ('PIL', 'Pillow 图像处理'),
    ('cryptography', '加密库'),
    ('yaml', 'YAML 解析'),
    ('anyio', '异步 IO'),
    ('h11', 'HTTP/1.1 协议'),
]

missing = []
installed = []

print("\n检查已安装的包:")
for package, description in required_packages:
    try:
        __import__(package)
        print(f"  ✅ {package:20s} - {description}")
        installed.append(package)
    except ImportError:
        print(f"  ❌ {package:20s} - {description} (未安装)")
        missing.append(package)

print(f"\n总结:")
print(f"  已安装: {len(installed)}/{len(required_packages)}")
print(f"  缺失: {len(missing)}/{len(required_packages)}")

if missing:
    print(f"\n❌ 缺少以下包，请安装:")
    print(f"  pip install {' '.join(missing)}")
    sys.exit(1)
else:
    print(f"\n✅ 所有依赖都已安装，可以开始打包！")
    print(f"\n打包命令:")
    print(f"  pyinstaller KMblogManager.spec")

print("\n" + "=" * 60)
