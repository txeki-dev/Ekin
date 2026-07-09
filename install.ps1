# Ekin Kanban Installer Script
# Ejecutar desde PowerShell con: irm https://raw.githubusercontent.com/txeki-dev/Ekin/main/install.ps1 | iex

# Configurar UTF-8 para consola para caracteres especiales
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "🚀 Iniciando instalación de Ekin Kanban..." -ForegroundColor Cyan

# 1. Comprobar requisitos
$pythonActive = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonActive) {
    Write-Error "❌ Python no está instalado en el sistema o no está en el PATH. Por favor, instala Python 3.10+ para continuar."
    exit
}

$gitActive = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitActive) {
    Write-Error "❌ Git no está instalado o no está en el PATH. Por favor, instala Git para continuar."
    exit
}

# 2. Definir ruta de instalación (Carpeta de usuario/EkinKanban)
$installDir = Join-Path $HOME "EkinKanban"
if (Test-Path $installDir) {
    Write-Host "📂 La carpeta de instalación ya existe en $installDir. Actualizando el código..." -ForegroundColor Yellow
    Set-Location $installDir
    git pull origin main
} else {
    Write-Host "📥 Clonando el repositorio desde GitHub..." -ForegroundColor Green
    git clone https://github.com/txeki-dev/Ekin.git $installDir
    Set-Location $installDir
}

# 3. Crear Entorno Virtual
if (-not (Test-Path "venv")) {
    Write-Host "⚙️ Creando el entorno virtual de Python..." -ForegroundColor Green
    python -m venv venv
}

# 4. Instalar dependencias
Write-Host "📦 Instalando PySide6..." -ForegroundColor Green
& ".\venv\Scripts\pip" install PySide6

# 5. Crear Script Lanzador silencioso (sin ventana de terminal)
$launchScript = @"
@echo off
cd /d "%~dp0"
start "" "venv\Scripts\pythonw.exe" main.py
"@
$launchScript | Out-File -FilePath "lanzar.bat" -Encoding ascii

# 6. Crear Acceso Directo en el Escritorio
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
    $Shortcut = $WshShell.CreateShortcut((Join-Path $DesktopPath "Ekin Kanban.lnk"))
    $Shortcut.TargetPath = (Join-Path $installDir "lanzar.bat")
    $Shortcut.WorkingDirectory = $installDir
    $Shortcut.IconLocation = (Join-Path $installDir "ekin_icon.png")
    $Shortcut.Description = "Ekin Kanban Board"
    $Shortcut.Save()
    Write-Host "✨ Acceso directo creado con éxito en tu Escritorio." -ForegroundColor Green
} catch {
    Write-Host "⚠️ No se pudo crear el acceso directo en el Escritorio automáticamente." -ForegroundColor Yellow
}

Write-Host "✅ ¡Instalación completada con éxito!" -ForegroundColor Green
Write-Host "Ubicación del software: $installDir" -ForegroundColor Green
Write-Host "Puedes iniciar el programa haciendo doble clic en el acceso directo de tu Escritorio o ejecutando lanzar.bat" -ForegroundColor Cyan
