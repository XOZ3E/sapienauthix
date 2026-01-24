@echo off
title Security Keystroke Monitor
color 0F

echo.
echo ==========================================================
echo    SYSTEM SECURITY MONITOR ACTIVATED
echo ==========================================================
echo.
echo Press Ctrl+C in this window to stop.
echo ----------------------------------------------------------

set "logfile=monitor_log.txt"
set "detected=0"

:WAIT_FOR_SHIFT
powershell -NoProfile -Command "Add-Type -AssemblyName PresentationCore, WindowsBase; if ([System.Windows.Input.Keyboard]::IsKeyDown([System.Windows.Input.Key]::LeftShift)) { exit 0 } else { Write-Host 'No monitored key pressed'; exit 1 }" 2>nul
if %ERRORLEVEL% equ 0 (
    set "detected=1"
) else (
    ping -n 1 -w 50 127.0.0.1 >nul
    goto WAIT_FOR_SHIFT
)

set CURRENT_TIME=%TIME%
set CURRENT_DATE=%DATE%
echo [%CURRENT_DATE% %CURRENT_TIME%] [ALERT] Left Shift Key Pressed.>>"%logfile%"
echo [!!! KEYBOARD VOILATION!!!]

:SPAM_POPUP
powershell -NoProfile -Command "$code='[DllImport(\"user32.dll\")]public static extern bool ShowWindow(IntPtr hWnd,int nCmdShow);[DllImport(\"user32.dll\")]public static extern bool SetForegroundWindow(IntPtr hWnd);';Add-Type -MemberDefinition $code -Name Win32 -Namespace Util;Add-Type -AssemblyName System.Windows.Forms;$form=New-Object System.Windows.Forms.Form;$form.TopMost=$true;$form.FormBorderStyle='FixedDialog';$form.StartPosition='CenterScreen';$form.Size=New-Object Drawing.Size(1920,1080);$form.Text='SYSTEM ACCESS VIOLATION';$form.BackColor = 'Red'; $form.ForeColor = 'Black'; $lbl.BackColor = 'Red'; $lbl.ForeColor = 'White';[System.Console]::Beep(800,1000);$lbl=New-Object System.Windows.Forms.Label;$lbl.Text='ACCESS DENIED: Keystroke Pattern Violation.';$lbl.AutoSize=$true;$lbl.Font = New-Object System.Drawing.Font('Arial', 50, [System.Drawing.FontStyle]::Bold);$lbl.Location=New-Object Drawing.Point(100,450);$form.Controls.Add($lbl);$null=$form.Show();[Util.Win32]::ShowWindow($form.Handle,5);[Util.Win32]::SetForegroundWindow($form.Handle);$form.ShowDialog()|Out-Null;Start-Sleep -Milliseconds 300;$form.Close()" >nul 2>&1
goto SPAM_POPUP