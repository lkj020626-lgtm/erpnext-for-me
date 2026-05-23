@echo off
chcp 65001 >nul
REM ============================================================
REM 星造 ERP 局域网批量部署脚本
REM 将 .exe 安装包静默安装到局域网内指定电脑
REM ============================================================
REM
REM 使用前准备：
REM   1. 先用 build-with-ip.sh 打包好 .exe（已内置服务器IP）
REM   2. 将 .exe 放到一个所有电脑能访问的共享文件夹
REM   3. 编辑下方的 INSTALLER_PATH 和 COMPUTERS.txt
REM   4. 确保你有目标电脑的管理员权限
REM
REM 注意：此脚本只会安装到 Windows 电脑，手机/平板不受影响
REM ============================================================

REM === 配置区 ===
SET INSTALLER_PATH=\\192.168.1.100\share\StarMakeERP-Setup.exe
SET DOMAIN_USER=administrator
SET DOMAIN_PASS=your_password

echo =========================================
echo   星造 ERP 局域网批量部署
echo =========================================
echo.
echo 安装包路径: %INSTALLER_PATH%
echo 目标电脑列表: computers.txt
echo.
echo 注意: 只会安装到 computers.txt 中列出的 Windows 电脑
echo       手机、平板、打印机等设备不会受到影响
echo.

REM 检查文件
if not exist computers.txt (
    echo [错误] 未找到 computers.txt 文件！
    echo.
    echo 请创建 computers.txt，每行一个电脑名或IP：
    echo   192.168.1.101
    echo   192.168.1.102
    echo   FRONT-DESK-PC
    echo   WAREHOUSE-PC
    echo.
    pause
    exit /b 1
)

echo 开始部署...
echo.

set SUCCESS=0
set FAIL=0

for /f "tokens=*" %%i in (computers.txt) do (
    echo [部署] %%i ...

    REM 方式1: PsExec（需要先下载 PsExec）
    REM psexec \\%%i -u %DOMAIN_USER% -p %DOMAIN_PASS% -c -f "%INSTALLER_PATH%" /S

    REM 方式2: WMIC 远程安装（适用于域环境）
    wmic /node:"%%i" /user:"%DOMAIN_USER%" /password:"%DOMAIN_PASS%" process call create "cmd /c start /wait \\%COMPUTERNAME%\share\StarMakeERP-Setup.exe /S" >nul 2>&1

    if errorlevel 1 (
        echo         [失败] %%i - 无法连接或安装失败
        set /a FAIL+=1
    ) else (
        echo         [成功] %%i
        set /a SUCCESS+=1
    )
)

echo.
echo =========================================
echo   部署完成
echo   成功: %SUCCESS% 台
echo   失败: %FAIL% 台
echo =========================================
pause
