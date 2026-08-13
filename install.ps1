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
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ 'git pull' ha fallado (¿cambios locales o conflicto?). La instalación existente en $installDir puede estar desactualizada o rota. Resuelve el error de git manualmente, o borra la carpeta $installDir y vuelve a ejecutar este instalador para clonar desde cero."
        exit
    }
} else {
    Write-Host "📥 Clonando el repositorio desde GitHub..." -ForegroundColor Green
    git clone https://github.com/txeki-dev/Ekin.git $installDir
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ 'git clone' ha fallado. Revisa tu conexión a internet y vuelve a intentarlo."
        exit
    }
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
$iconPath = Join-Path $installDir "ekin_icon.ico"
if (-not (Test-Path $iconPath)) {
    Write-Host "⚠️ No se encontró ekin_icon.ico en $installDir tras clonar/actualizar -- el acceso directo se creará sin icono personalizado (Windows mostrará un icono genérico). Esto indica que la copia local del repositorio está incompleta." -ForegroundColor Yellow
}
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
    $Shortcut = $WshShell.CreateShortcut((Join-Path $DesktopPath "Ekin Kanban.lnk"))
    $Shortcut.TargetPath = (Join-Path $installDir "lanzar.bat")
    $Shortcut.WorkingDirectory = $installDir
    if (Test-Path $iconPath) {
        $Shortcut.IconLocation = "$iconPath,0"
    }
    $Shortcut.Description = "Ekin Kanban Board"
    $Shortcut.Save()
    Write-Host "✨ Acceso directo creado con éxito en tu Escritorio." -ForegroundColor Green
} catch {
    Write-Host "⚠️ No se pudo crear el acceso directo en el Escritorio automáticamente." -ForegroundColor Yellow
}

Write-Host "✅ ¡Instalación completada con éxito!" -ForegroundColor Green
Write-Host "Ubicación del software: $installDir" -ForegroundColor Green
Write-Host "Puedes iniciar el programa haciendo doble clic en el acceso directo de tu Escritorio o ejecutando lanzar.bat" -ForegroundColor Cyan
