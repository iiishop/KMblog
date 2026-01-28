# Auto release script (Windows PowerShell)
# Usage: .\scripts\release.ps1 [version] [-Force]

param(
    [Parameter(Mandatory = $false)]
    [string]$Version,
    
    [Parameter(Mandatory = $false)]
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# If no version provided, read current version and recommend
if (-not $Version) {
    if (Test-Path "VERSION") {
        $currentVersion = Get-Content "VERSION" -Raw
        $currentVersion = $currentVersion.Trim()
        
        # Parse version number
        if ($currentVersion -match '^(\d+)\.(\d+)\.(\d+)$') {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            $patch = [int]$matches[3]
            
            # Recommend version numbers
            $patchVersion = "$major.$minor.$($patch + 1)"
            $minorVersion = "$major.$($minor + 1).0"
            $majorVersion = "$($major + 1).0.0"
            
            Write-Host "==========================================" -ForegroundColor Cyan
            Write-Host "Current version: $currentVersion" -ForegroundColor Yellow
            Write-Host "==========================================" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Recommended versions:" -ForegroundColor Green
            Write-Host "  1. $patchVersion (bug fix)" -ForegroundColor White
            Write-Host "  2. $minorVersion (new feature)" -ForegroundColor White
            Write-Host "  3. $majorVersion (major update)" -ForegroundColor White
            Write-Host ""
            Write-Host "Usage examples:" -ForegroundColor Cyan
            Write-Host "  .\scripts\release.ps1 $patchVersion" -ForegroundColor Gray
            Write-Host "  .\scripts\release.ps1 $minorVersion" -ForegroundColor Gray
            Write-Host "  .\scripts\release.ps1 $majorVersion" -ForegroundColor Gray
            Write-Host ""
            exit 0
        }
        else {
            Write-Host "Error: Invalid VERSION file format: $currentVersion" -ForegroundColor Red
            Write-Host "Please specify version manually: .\scripts\release.ps1 1.0.0" -ForegroundColor Cyan
            exit 1
        }
    }
    else {
        Write-Host "Error: VERSION file not found" -ForegroundColor Red
        Write-Host "Please specify initial version: .\scripts\release.ps1 1.0.0" -ForegroundColor Cyan
        exit 1
    }
}

$Tag = "v$Version"

# Validate version format
if ($Version -notmatch '^\d+\.\d+\.\d+$') {
    Write-Host "Error: Invalid version format, should be x.y.z (e.g. 1.0.1)" -ForegroundColor Red
    exit 1
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Preparing release: $Version" -ForegroundColor Cyan
if ($Force) {
    Write-Host "Mode: Force release (overwrite existing tag)" -ForegroundColor Yellow
}
Write-Host "==========================================" -ForegroundColor Cyan

# Check if VERSION file needs update
$needsVersionUpdate = $false
if (Test-Path "VERSION") {
    $currentVersion = Get-Content "VERSION" -Raw
    $currentVersion = $currentVersion.Trim()
    if ($currentVersion -ne $Version) {
        $needsVersionUpdate = $true
        Write-Host "VERSION file needs update: $currentVersion -> $Version" -ForegroundColor Yellow
    }
    else {
        Write-Host "VERSION file is up to date: $Version" -ForegroundColor Green
    }
}
else {
    $needsVersionUpdate = $true
    Write-Host "VERSION file not found, will create" -ForegroundColor Yellow
}

# Check for uncommitted changes (excluding VERSION file)
Write-Host "Checking Git status..." -ForegroundColor Yellow
$status = git status --porcelain

# Filter out VERSION file changes
$statusWithoutVersion = $status | Where-Object { $_ -notmatch 'VERSION' }

if ($statusWithoutVersion) {
    Write-Host ""
    Write-Host "Error: Uncommitted changes detected (excluding VERSION file)!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Uncommitted files:" -ForegroundColor Yellow
    $statusWithoutVersion | ForEach-Object { Write-Host "  $_" }
    Write-Host ""
    Write-Host "Please commit all changes first:" -ForegroundColor Cyan
    Write-Host "  git add ."
    Write-Host "  git commit -m `"your commit message`""
    Write-Host ""
    Write-Host "Then run the release script again." -ForegroundColor Cyan
    exit 1
}

Write-Host "Git status check passed" -ForegroundColor Green

# Check if tag exists
Write-Host "Checking if tag exists..." -ForegroundColor Yellow
$tagExists = $false
try {
    git rev-parse $Tag 2>$null | Out-Null
    $tagExists = $true
}
catch {
    $tagExists = $false
}

if ($tagExists) {
    if ($Force) {
        Write-Host "Tag $Tag exists, will force overwrite" -ForegroundColor Yellow
        
        # Delete local tag
        Write-Host "  Deleting local tag..." -ForegroundColor Gray
        git tag -d $Tag
        
        # Try to delete remote tag
        Write-Host "  Deleting remote tag..." -ForegroundColor Gray
        try {
            git push origin ":refs/tags/$Tag" 2>$null
            Write-Host "  Remote tag deleted" -ForegroundColor Green
        }
        catch {
            Write-Host "  Remote tag not found or already deleted" -ForegroundColor Gray
        }
    }
    else {
        Write-Host ""
        Write-Host "Error: Tag $Tag already exists" -ForegroundColor Red
        Write-Host ""
        Write-Host "Option 1: Use -Force parameter to overwrite" -ForegroundColor Cyan
        Write-Host "  .\scripts\release.ps1 $Version -Force"
        Write-Host ""
        Write-Host "Option 2: Delete tag manually" -ForegroundColor Cyan
        Write-Host "  git tag -d $Tag"
        Write-Host "  git push origin :refs/tags/$Tag"
        Write-Host ""
        exit 1
    }
}
else {
    Write-Host "Tag check passed" -ForegroundColor Green
}

Write-Host ""

# Update VERSION file if needed
if ($needsVersionUpdate) {
    Write-Host "1. Updating VERSION file..." -ForegroundColor Yellow
    Set-Content -Path "VERSION" -Value $Version -NoNewline
    git add VERSION
    
    Write-Host "2. Committing VERSION file..." -ForegroundColor Yellow
    git commit -m "chore: bump version to $Version"
    
    $needsPush = $true
}
else {
    Write-Host "1. VERSION file up to date, skipping" -ForegroundColor Gray
    $needsPush = $false
}

# Create tag
Write-Host "2. Creating Git tag..." -ForegroundColor Yellow
git tag -a $Tag -m "Release $Version"

# Check if code push is needed
if ($needsPush) {
    Write-Host "3. Pushing to GitHub..." -ForegroundColor Yellow
    Write-Host "   Pushing code..." -ForegroundColor Gray
    git push origin main
}
else {
    # Check if local is ahead of remote
    $localCommit = git rev-parse HEAD
    $remoteCommit = git rev-parse origin/main 2>$null
    
    if ($localCommit -ne $remoteCommit) {
        Write-Host "3. Pushing to GitHub..." -ForegroundColor Yellow
        Write-Host "   Local commits detected" -ForegroundColor Gray
        Write-Host "   Pushing code..." -ForegroundColor Gray
        git push origin main
    }
    else {
        Write-Host "3. Code is up to date, skipping push" -ForegroundColor Gray
    }
}

# Push tag
Write-Host "4. Pushing tag..." -ForegroundColor Yellow
if ($Force) {
    git push origin $Tag --force
}
else {
    git push origin $Tag
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Version $Version released successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "GitHub Actions will automatically build and publish the new version" -ForegroundColor Cyan
Write-Host "View build progress: https://github.com/iiishop/KMblog/actions" -ForegroundColor Cyan
Write-Host ""
