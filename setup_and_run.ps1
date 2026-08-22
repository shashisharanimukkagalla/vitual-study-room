param(
    [switch]$CreateAdmin,
    [switch]$Production,
    [switch]$NoStart,
    [string]$HostName = "127.0.0.1",
    [int]$Port = 5000
)

$ErrorActionPreference = "Stop"

function Write-Step($Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Invoke-Checked {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $FilePath $($Arguments -join ' ')"
    }
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Step "Checking Python"
$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    throw "Python is not installed or not available in PATH. Install Python 3.11+ from https://www.python.org/downloads/ and rerun this script."
}

$VersionText = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$Version = [version]$VersionText
if ($Version -lt [version]"3.11") {
    throw "Python 3.11+ is required. Found Python $VersionText."
}

Write-Step "Creating virtual environment"
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment was not created correctly."
}

Write-Step "Installing dependencies"
Invoke-Checked $VenvPython @("-m", "pip", "install", "--upgrade", "pip")
Invoke-Checked $VenvPython @("-m", "pip", "install", "-r", "requirements.txt")

Write-Step "Preparing environment file"
$SqlitePath = (Join-Path $Root "instance\study_hall.db").Replace("\", "/")
$DatabaseUrl = "sqlite:///$SqlitePath"
if (-not (Test-Path ".env")) {
    $Secret = & $VenvPython -c "import secrets; print(secrets.token_urlsafe(48))"
@"
SECRET_KEY=$Secret
DATABASE_URL=$DatabaseUrl
FLASK_DEBUG=false
SESSION_COOKIE_SECURE=false
SOCKETIO_CORS_ALLOWED_ORIGINS=
"@ | Set-Content -Path ".env" -Encoding ASCII
    Write-Host "Created .env with a generated SECRET_KEY."
} else {
    $EnvText = Get-Content ".env" -Raw
    if ($EnvText -match "DATABASE_URL=sqlite:///instance/study_hall.db") {
        $EnvText = $EnvText -replace "DATABASE_URL=sqlite:///instance/study_hall.db", "DATABASE_URL=$DatabaseUrl"
        Set-Content -Path ".env" -Value $EnvText -Encoding ASCII
        Write-Host "Updated .env to use an absolute SQLite database path."
    }
    Write-Host ".env already exists; keeping current settings."
}

Write-Step "Initializing database"
$env:FLASK_APP = "run.py"
Invoke-Checked $VenvPython @("-m", "flask", "init-db")

if ($CreateAdmin) {
    Write-Step "Creating admin user"
    Invoke-Checked $VenvPython @("-m", "flask", "create-admin")
}

if ($NoStart) {
    Write-Step "Setup complete"
    Write-Host "Run setup_and_run.bat to start the app."
    exit 0
}

Write-Step "Starting Virtual Study Hall"
$env:HOST = $HostName
$env:PORT = "$Port"

if ($Production) {
    Write-Host "Production-style server: http://$HostName`:$Port"
    Invoke-Checked $VenvPython @("-m", "waitress", "--listen=$HostName`:$Port", "wsgi:app")
} else {
    $env:FLASK_DEBUG = "false"
    Write-Host "Local server: http://$HostName`:$Port"
    Invoke-Checked $VenvPython @("run.py")
}
