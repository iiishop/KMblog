@echo off
chcp 65001 >nul
echo ======================================
echo KMBlog 管理工具打包脚本
echo ======================================
echo.

echo 正在检查 Flet 是否安装...
python -c "import flet" 2>nul
if errorlevel 1 (
    echo Flet 未安装，正在安装...
    pip install flet
    echo.
)

echo 开始打包...
echo.

flet pack blog_manager.py --name "KMBlog管理工具"

if errorlevel 0 (
    echo.
    echo ======================================
    echo 打包成功！
    echo ======================================
    echo.
    echo exe 文件位置: dist\KMBlog管理工具.exe
    echo.
    echo 请将 exe 文件复制到项目根目录使用
    echo.
) else (
    echo.
    echo ======================================
    echo 打包失败！请查看上方错误信息
    echo ======================================
    echo.
)

pause
