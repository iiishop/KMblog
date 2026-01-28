#!/bin/bash
# 自动发布脚本
# 用法: ./scripts/release.sh 1.0.1

set -e

# 检查参数
if [ -z "$1" ]; then
    echo "错误: 请提供版本号"
    echo "用法: ./scripts/release.sh 1.0.1"
    exit 1
fi

VERSION=$1
TAG="v$VERSION"

# 验证版本号格式
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "错误: 版本号格式不正确，应为 x.y.z (如 1.0.1)"
    exit 1
fi

echo "=========================================="
echo "准备发布版本: $VERSION"
echo "=========================================="

# 检查是否有未提交的更改
echo "检查 Git 状态..."
if ! git diff-index --quiet HEAD --; then
    echo ""
    echo "错误: 检测到未提交的更改！"
    echo ""
    echo "未提交的文件:"
    git status --short
    echo ""
    echo "请先提交所有更改:"
    echo "  git add ."
    echo "  git commit -m \"your commit message\""
    echo ""
    echo "然后再运行发布脚本。"
    exit 1
fi

echo "✓ Git 状态检查通过"

# 检查 tag 是否已存在
echo "检查标签是否存在..."
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo ""
    echo "错误: Tag $TAG 已存在"
    echo ""
    echo "如果要重新发布，请先删除标签:"
    echo "  git tag -d $TAG"
    echo "  git push origin :refs/tags/$TAG"
    exit 1
fi

echo "✓ 标签检查通过"
echo ""

# 更新 VERSION 文件
echo "1. 更新 VERSION 文件..."
echo "$VERSION" > VERSION
git add VERSION

# 提交 VERSION 文件
echo "2. 提交 VERSION 文件..."
git commit -m "chore: bump version to $VERSION"

# 创建 tag
echo "3. 创建 Git tag..."
git tag -a "$TAG" -m "Release $VERSION"

# 推送到远程
echo "4. 推送到 GitHub..."
echo "   推送代码..."
git push origin main

echo "   推送标签..."
git push origin "$TAG"

echo ""
echo "=========================================="
echo "✓ 版本 $VERSION 发布成功！"
echo "=========================================="
echo ""
echo "GitHub Actions 将自动构建并发布新版本"
echo "查看构建进度: https://github.com/iiishop/KMblog/actions"
echo ""
