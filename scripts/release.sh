#!/bin/bash
# 自动发布脚本
# 用法: ./scripts/release.sh [版本号] [选项]
# 选项:
#   --force         强制覆盖已存在的标签
#   -d "描述"       指定 release notes（支持多行）
#   --changelog     从 git log 自动生成 changelog
# 
# 示例:
#   ./scripts/release.sh 1.0.1
#   ./scripts/release.sh 1.0.1 -d "修复了若干 bug"
#   ./scripts/release.sh 1.0.1 --changelog
#   ./scripts/release.sh 1.0.1 -d "新功能：\n- 添加了编辑器\n- 优化了性能"

set -e

# 解析参数
VERSION=""
FORCE=false
DESCRIPTION=""
USE_CHANGELOG=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        -d)
            DESCRIPTION="$2"
            shift 2
            ;;
        --changelog)
            USE_CHANGELOG=true
            shift
            ;;
        *)
            VERSION="$1"
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
local_tag_exists=false
remote_tag_exists=false

if git rev-parse "$TAG" >/dev/null 2>&1; then
    local_tag_exists=true
fi

if git ls-remote --tags origin | grep -q "refs/tags/$TAG$"; then
    remote_tag_exists=true
fi

if [ "$local_tag_exists" = true ] || [ "$remote_tag_exists" = true ]; then
    if [ "$FORCE" = true ]; then
        echo "⚠ Tag $TAG 已存在，将强制覆盖"
        
        # 删除本地 tag
        if [ "$local_tag_exists" = true ]; then
            echo "  删除本地标签..."
            git tag -d "$TAG"
        fi
        
        # 删除远程 tag
        if [ "$remote_tag_exists" = true ]; then
            echo "  删除远程标签..."
            if git push origin ":refs/tags/$TAG" 2>/dev/null; then
                echo "  ✓ 远程标签已删除"
            else
                echo "  ⚠ 远程标签删除失败（可能需要手动删除）"
            fi
        fi
    else
        echo ""
        if [ "$local_tag_exists" = true ] && [ "$remote_tag_exists" = false ]; then
            echo "⚠ 检测到本地标签存在但远程不存在（可能是上次推送失败）"
            echo ""
            echo "选项 1: 使用 --force 参数重新创建并推送"
            echo "  ./scripts/release.sh $VERSION --force -d \"$DESCRIPTION\""
            echo ""
            echo "选项 2: 直接推送现有标签"
            echo "  git push origin $TAG"
            echo ""
            echo "选项 3: 手动删除本地标签后重试"
            echo "  git tag -d $TAG"
            echo "  ./scripts/release.sh $VERSION"
            echo ""
        else
            echo "错误: Tag $TAG 已存在"
            echo ""
            echo "选项 1: 使用 --force 参数强制覆盖"
            echo "  ./scripts/release.sh $VERSION --force"
            echo ""
            echo "选项 2: 手动删除标签"
            echo "  git tag -d $TAG"
            echo "  git push origin :refs/tags/$TAG"
            echo ""
        fi
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
    
    # 构建 commit message
    commit_msg="chore: bump version to $VERSION"
    if [ -n "$DESCRIPTION" ]; then
        commit_msg="$commit_msg

$DESCRIPTION"
    fi
    
    git commit -m "$commit_msg"
    
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
max_retries=3
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if [ "$FORCE" = true ]; then
        if git push origin "$TAG" --force; then
            echo "✓ 标签推送成功"
            break
        fi
    else
        if git push origin "$TAG"; then
            echo "✓ 标签推送成功"
            break
        fi
    fi
    
    retry_count=$((retry_count + 1))
    if [ $retry_count -lt $max_retries ]; then
        echo "⚠ 推送失败，重试 $retry_count/$max_retries..."
        sleep 2
    else
        echo ""
        echo "❌ 标签推送失败（已重试 $max_retries 次）"
        echo ""
        echo "可能的原因:"
        echo "  1. 网络连接问题"
        echo "  2. GitHub 访问受限"
        echo ""
        echo "解决方案:"
        echo "  1. 检查网络连接后手动推送:"
        echo "     git push origin $TAG"
        echo ""
        echo "  2. 或稍后重新运行脚本:"
        echo "     ./scripts/release.sh $VERSION --force"
        echo ""
        exit 1
    fi
done

# 生成 release notes
echo "5. 准备 release notes..."
RELEASE_NOTES=""

if [ -n "$DESCRIPTION" ]; then
    # 使用用户提供的描述
    RELEASE_NOTES="$DESCRIPTION"
    echo "   使用自定义描述"
elif [ "$USE_CHANGELOG" = true ]; then
    # 从 git log 生成 changelog
    echo "   从 git log 生成 changelog..."
    
    # 获取上一个 tag
    PREV_TAG=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")
    
    if [ -n "$PREV_TAG" ]; then
        echo "   对比版本: $PREV_TAG -> $TAG"
        RELEASE_NOTES="## Changes since $PREV_TAG\n\n"
        RELEASE_NOTES+=$(git log $PREV_TAG..HEAD --pretty=format:"- %s (%h)" --no-merges)
    else
        echo "   未找到上一个 tag，生成完整 changelog"
        RELEASE_NOTES="## Initial Release\n\n"
        RELEASE_NOTES+=$(git log --pretty=format:"- %s (%h)" --no-merges | head -20)
    fi
else
    # 默认描述
    RELEASE_NOTES="Release $VERSION\n\nSee commits for details."
    echo "   使用默认描述"
fi

# 创建 GitHub Release
echo "6. 创建 GitHub Release..."

# 检查是否安装了 gh CLI
if command -v gh &> /dev/null; then
    echo "   使用 GitHub CLI 创建 release..."
    
    # 将 \n 转换为真正的换行符
    RELEASE_NOTES_FORMATTED=$(echo -e "$RELEASE_NOTES")
    
    # 创建 release
    if gh release create "$TAG" \
        --title "Release $VERSION" \
        --notes "$RELEASE_NOTES_FORMATTED" \
        --verify-tag; then
        echo "   ✓ GitHub Release 创建成功"
    else
        echo "   ⚠ GitHub Release 创建失败（可能需要手动创建）"
        echo ""
        echo "   Release Notes:"
        echo "   ----------------------------------------"
        echo -e "$RELEASE_NOTES_FORMATTED"
        echo "   ----------------------------------------"
    fi
else
    echo "   ⚠ 未安装 GitHub CLI (gh)"
    echo "   请手动在 GitHub 上创建 release，或安装 gh CLI:"
    echo "   https://cli.github.com/"
    echo ""
    echo "   Release Notes:"
    echo "   ----------------------------------------"
    echo -e "$RELEASE_NOTES"
    echo "   ----------------------------------------"
fi

echo ""
echo "=========================================="
echo "✓ 版本 $VERSION 发布成功！"
echo "=========================================="
echo ""
echo "GitHub Actions 将自动构建并发布新版本"
echo "查看构建进度: https://github.com/iiishop/KMblog/actions"
echo "查看 Release: https://github.com/iiishop/KMblog/releases/tag/$TAG"
echo ""
