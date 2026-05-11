# export_to_flash.ps1

$source = "C:\Users\d\PycharmProjects\videohosting"
$destination = "E:\lampix"  # поменяй E: на букву своей флешки

Write-Host "Копирую проект на флешку..." -ForegroundColor Green
Write-Host "Источник: $source" -ForegroundColor Yellow
Write-Host "Назначение: $destination" -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path $destination | Out-Null

robocopy $source $destination /E /XD ".git" "__pycache__" "demo_videos" /XF "*.pyc" "*.log" /TEE /NP

Write-Host ""
Write-Host "Готово!" -ForegroundColor Green

$size = (Get-ChildItem $destination -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Размер: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan

Write-Host ""
Write-Host "Проверка:" -ForegroundColor Yellow

if (Test-Path "$destination\instance\lampix.db") {
    Write-Host "  БД - OK" -ForegroundColor Green
} else {
    Write-Host "  БД - НЕ НАЙДЕНА!" -ForegroundColor Red
}

if (Test-Path "$destination\.env") {
    Write-Host "  .env - OK" -ForegroundColor Green
} else {
    Write-Host "  .env - НЕ НАЙДЕН!" -ForegroundColor Red
}

if (Test-Path "$destination\ffmpeg") {
    Write-Host "  FFmpeg - OK" -ForegroundColor Green
} else {
    Write-Host "  FFmpeg - НЕ НАЙДЕН" -ForegroundColor Yellow
}

$videoCount = (Get-ChildItem "$destination\app\static\uploads\videos" -Filter "*.mp4" -ErrorAction SilentlyContinue).Count
Write-Host "  Видео: $videoCount файлов" -ForegroundColor Green

if (Test-Path "$destination\.venv") {
    Write-Host "  .venv - OK" -ForegroundColor Green
} else {
    Write-Host "  .venv - НЕ НАЙДЕН" -ForegroundColor Yellow
}