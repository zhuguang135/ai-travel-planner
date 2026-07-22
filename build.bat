@echo off
chcp 65001 >nul
title 打包 逐光

echo ============================================
echo  打包 逐光 (Streamlit → .exe)
echo  最小化构建，仅含必需依赖
echo ============================================
echo.

REM 安装/更新依赖
echo [1/3] 安装依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 安装依赖失败，请检查网络连接
    pause
    exit /b 1
)

REM 安装 PyInstaller 和 UPX（如果没装）
echo [2/3] 安装构建工具...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo 安装 PyInstaller 失败
    pause
    exit /b 1
)

REM 打包
echo [3/3] 正在打包，请耐心等待（约3-10分钟）...
echo.

pyinstaller package.spec --clean

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo  打包成功！
    echo  输出目录: dist\逐光\
    echo  执行文件: dist\逐光\逐光.exe
    echo ============================================
    echo.
    echo  使用方式：双击 逐光.exe 即可运行
    echo  首次启动会弹出浏览器窗口，稍等片刻即可
    echo.
    echo  注意：打包体积取决于已安装的依赖大小
    echo  可以通过 pip 安装最小依赖来减小体积
    echo ============================================
) else (
    echo.
    echo 打包失败，请检查错误信息
)

pause