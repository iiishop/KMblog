# 自动发布脚本 (Windows PowerShell)
# 用法: .\scripts\release.ps1 1.0.1

param(
    [Parameter(Mandatory = $true)]
    [string]$Version
)

$ErrorActionPreference = "Stop"

$Tag = "v$Version"

# 验证版本号格式
if ($Version -notmatch '^\d+\.\d+\.\d+$') {
    Write-Host "错误: 版本号格式不正确，应为 x.y.z (如 1.0.1)" -ForegroundColor Red
    exit 1
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "准备发布版本: $Version" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 检查是否有未提交的更改
Write-Host "检查 Git 状态..." -ForegroundColor Yellow
$status = git status --porcelain
if ($status) {
    Write-Host ""
    Write-Host "错误: 检测到未提交的更改！" -ForegroundColor Red
    Write-Host ""
    Write-Host "未提交的文件:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    Write-Host "请先提交所有更改:" -ForegroundColor Cyan
    Write-Host "  git add ."
    Write-Host "  git commit -m `"your commit message`""
    Write-Host ""
    Write-Host "然后再运行发布脚本。" -ForegroundColor Cyan
    exit 1
}

Write-Host "✓ Git 状态检查通过" -ForegroundColor Green

# 检查 tag 是否已存在
Write-Host "检查标签是否存在..." -ForegroundColor Yellow
try {
    git rev-parse $Tag 2>$null
    Write-Host ""
    Write-Host "错误: Tag $Tag 已存在" -ForegroundColor Red
    Write-Host ""
    Write-Host "如果要重新发布，请先删除标签:" -ForegroundColor Cyan
    Write-Host "  git tag -d $Tag"
    Write-Host "  git push origin :refs/tags/$Tag"
    exit 1
}
catch {
    # Tag 不存在，继续
    Write-Host "✓ 标签检查通过" -ForegroundColor Green
}

Write-Host ""

# 更新 VERSION 文件
Write-Host "1. 更新 VERSION 文件..." -ForegroundColor Yellow
Set-Content -Path "VERSION" -Value $Version -NoNewline
git add VERSION

# 提交 VERSION 文件
Write-Host "2. 提交 VERSION 文件..." -ForegroundColor Yellow
git commit -m "chore: bump version to $Version"

# 创建 tag
Write-Host "3. 创建 Git tag..." -ForegroundColor Yellow
git tag -a $Tag -m "Release $Version"

# 推送到远程
Write-Host "4. 推送到 GitHub..." -ForegroundColor Yellow
Write-Host "   推送代码..." -ForegroundColor Gray
git push origin main

Write-Host "   推送标签..." -ForegroundColor Gray
git push origin $Tag

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✓ 版本 $Version 发布成功！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "GitHub Actions 将自动构建并发布新版本" -ForegroundColor Cyan
Write-Host "查看构建进度: https://github.com/iiishop/KMblog/actions" -ForegroundColor Cyan
Write-Host ""
