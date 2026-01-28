# 停止所有 Python 進程 (排除當前腳本)
$processes = Get-Process | Where-Object {$_.ProcessName -like '*python*'}

if ($processes) {
    Write-Host "找到 $($processes.Count) 個 Python 進程:"
    $processes | ForEach-Object {
        Write-Host "  PID: $($_.Id), Name: $($_.ProcessName), StartTime: $($_.StartTime)"
    }

    Write-Host "`n正在停止所有 Python 進程..."
    $processes | ForEach-Object {
        try {
            Stop-Process -Id $_.Id -Force
            Write-Host "  [OK] 已停止 PID: $($_.Id)"
        } catch {
            Write-Host "  [ERROR] 無法停止 PID: $($_.Id)"
        }
    }

    Write-Host "`n完成!"
} else {
    Write-Host "沒有找到 Python 進程"
}
