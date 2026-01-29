#!/bin/bash
# 自动发布脚本
# 用法: ./scripts/release.sh [版本号] [--force]
# 如果不提供版本号，脚本会自动推荐下一个版本

set -e

# 解析参数
VERSION=""
FORCE=false

for arg in "$@"; do
    case $arg in
        --force)
            FORCE=true
            shift
            ;;
        *)
            VERSION="$arg"
            shift
            ;;
    esac
done

# 如果没有提供版本号，读取当前版本并推荐
if [ -z "$VERSION" ]; then
    if [ -f "VERSION" ]; then
        current_version=$(cat VERSION)
        
        # 解析版本号
        if [[ $current_version =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
            major="${BASH_REMATCH[1]}"
            minor="${BASH_REMATCH[2]}"
            patch="${BASH_REMATCH[3]}"
            
            # 推荐版本号
            patch_version="$major.$minor.$((patch + 1))"
            minor_version="$major.$((minor + 1)).0"
            major_version="$((major + 1)).0.0"
            
            echo "=========================================="
            echo "当前版本: $current_version"
            echo "=========================================="
            echo ""
            echo "推荐的版本号:"
            echo "  1. $patch_version (修复 bug)"
            echo "  2. $minor_version (新功能)"
            echo "  3. $major_version (重大更新)"
            echo ""
            echo "用法示例:"
            echo "  ./scripts/release.sh $patch_version"
            echo "  ./scripts/release.sh $minor_version"
            echo "  ./scripts/release.sh $major_version"
            echo ""
            exit 0
        else
            echo "错误: VERSION 文件格式不正确: $current_version"
            echo "请手动指定版本号: ./scripts/release.sh 1.0.0"
            exit 1
        fi
    else
        echo "错误: VERSION 文件不存在"
        echo "请指定初始版本号: ./scripts/release.sh 1.0.0"
        exit 1
    fi
fi

TAG="v$VERSION"

# 验证版本号格式
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "错误: 版本号格式不正确，应为 x.y.z (如 1.0.1)"
    exit 1
fi

echo "=========================================="
echo "准备发布版本: $VERSION"
if [ "$FORCE" = true ]; then
    echo "模式: 强制发布（覆盖已存在的标签）"
fi
echo "=========================================="

# 检查 VERSION 文件是否需要更新
needs_version_update=false
if [ -f "VERSION" ]; then
    current_version=$(cat VERSION)
    if [ "$current_version" != "$VERSION" ]; then
        needs_version_update=true
        echo "检测到 VERSION 文件需要更新: $current_version -> $VERSION"
    else
        echo "VERSION 文件已是最新: $VERSION"
    fi
else
    needs_version_update=true
    echo "VERSION 文件不存在，将创建"
fi

# 检查是否有未提交的更改（排除 VERSION 文件）
echo "检查 Git 状态..."
status=$(git status --porcelain | grep -v "VERSION" || true)

if [ -n "$status" ]; then
    echo ""
    echo "错误: 检测到未提交的更改（除 VERSION 文件外）！"
    echo ""
    echo "未提交的文件:"
    echo "$status"
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
tag_exists=false
if git rev-parse "$TAG" >/dev/null 2>&1; then
    tag_exists=true
fi

if [ "$tag_exists" = true ]; then
    if [ "$FORCE" = true ]; then
        echo "⚠ Tag $TAG 已存在，将强制覆盖"
        
        # 删除本地 tag
        echo "  删除本地标签..."
        git tag -d "$TAG"
        
        # 尝试删除远程 tag
        echo "  删除远程标签..."
        if git push origin ":refs/tags/$TAG" 2>/dev/null; then
            echo "  ✓ 远程标签已删除"
        else
            echo "  ℹ 远程标签不存在或已删除"
        fi
    else
        echo ""
        echo "错误: Tag $TAG 已存在"
        echo ""
        echo "选项 1: 使用 --force 参数强制覆盖"
        echo "  ./scripts/release.sh $VERSION --force"
        echo ""
        echo "选项 2: 手动删除标签"
        echo "  git tag -d $TAG"
        echo "  git push origin :refs/tags/$TAG"
        echo ""
        exit 1
    fi
else
    echo "✓ 标签检查通过"
fi

echo ""

# 如果需要更新 VERSION 文件
if [ "$needs_version_update" = true ]; then
    echo "1. 更新 VERSION 文件..."
    echo "$VERSION" > VERSION
    git add VERSION
    
    echo "2. 提交 VERSION 文件..."
    git commit -m "chore: bump version to $VERSION"
    
    needs_push=true
else
    echo "1. VERSION 文件无需更新，跳过"
    needs_push=false
fi

# 创建 tag
echo "2. 创建 Git tag..."
git tag -a "$TAG" -m "Release $VERSION"

# 检查是否需要推送代码
if [ "$needs_push" = true ]; then
    echo "3. 推送到 GitHub..."
    echo "   推送代码..."
    git push origin main
else
    # 检查本地是否领先远程
    local_commit=$(git rev-parse HEAD)
    remote_commit=$(git rev-parse origin/main 2>/dev/null || echo "")
    
    if [ "$local_commit" != "$remote_commit" ]; then
        echo "3. 推送到 GitHub..."
        echo "   检测到本地有未推送的提交"
        echo "   推送代码..."
        git push origin main
    else
        echo "3. 代码已是最新，跳过推送"
    fi
fi

# 推送标签
echo "4. 推送标签..."
if [ "$FORCE" = true ]; then
    git push origin "$TAG" --force
else
    git push origin "$TAG"
fi

echo ""
echo "=========================================="
echo "✓ 版本 $VERSION 发布成功！"
echo "=========================================="
echo ""
echo "GitHub Actions 将自动构建并发布新版本"
echo "查看构建进度: https://github.com/iiishop/KMblog/actions"
echo ""
