<#
Helper script to prepare a Windows dev machine for this project.
- Installs Python using winget (if available)
- Installs pip packages from requirements.txt
- Optionally generates a Fernet ENCRYPTION_KEY and sets it for the current session
- Can run encryption/decryption commands

Usage (PowerShell run as Administrator if installing Python):
    .\install_windows.ps1

Follow interactive prompts.
#>

function Prompt-YesNo($msg, $defaultYes = $true) {
    $yn = Read-Host "$msg [Y/n]"
    if ([string]::IsNullOrWhiteSpace($yn)) { return $defaultYes }
    return $yn -match '^(y|Y)'
}

Write-Host "=== Project Windows Setup Helper ===" -ForegroundColor Cyan

# Check for python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        if (Prompt-YesNo "Python not found. Install Python 3 via winget now?") {
            Write-Host "Installing Python 3 via winget..." -ForegroundColor Yellow
            winget install --id Python.Python.3 -e --source winget
            if ($LASTEXITCODE -ne 0) { Write-Warning "winget install reported a non-zero exit code." }
        } else {
            Write-Host "Please install Python 3.11+ manually and ensure 'python' is on PATH." -ForegroundColor Yellow
            return
        }
    } else {
        Write-Host "winget not found. Please install Python 3 manually from https://www.python.org/downloads/windows and re-run this script." -ForegroundColor Yellow
        return
    }
} else {
    Write-Host "Found Python: $($python.Path)" -ForegroundColor Green
}

# Ensure pip and upgrade
Write-Host "Upgrading pip and wheel..." -ForegroundColor Cyan
python -m pip install --upgrade pip wheel setuptools

# Install requirements
if (Test-Path requirements.txt) {
    if (Prompt-YesNo "Install Python dependencies from requirements.txt?") {
        python -m pip install -r requirements.txt
    }
} else {
    Write-Warning "requirements.txt not found in current directory. Skipping pip install."
}

# Generate or set ENCRYPTION_KEY
if (Prompt-YesNo "Generate a new ENCRYPTION_KEY now?") {
    $key = python crypto_utils.py generate-key 2>$null
    if (-not $key) {
        # try direct generation
        $key = python - <<'PY'
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
PY
    }
    $key = $key -replace "Generated ENCRYPTION_KEY:\s*", "" -replace "\r|\n", ""
    Write-Host "Generated key: $key" -ForegroundColor Green
    if (Prompt-YesNo "Set ENCRYPTION_KEY for this PowerShell session (not permanent)?") {
        $env:ENCRYPTION_KEY = $key
        Write-Host "ENCRYPTION_KEY set for current session." -ForegroundColor Green
    }
    if (Prompt-YesNo "Persist ENCRYPTION_KEY to your user environment variables (setx)?") {
        setx ENCRYPTION_KEY $key | Out-Null
        Write-Host "ENCRYPTION_KEY persisted to user environment variables. You may need to open a new shell." -ForegroundColor Green
    }
} else {
    Write-Host "Skipping key generation. Ensure ENCRYPTION_KEY is set in your environment before encrypt/decrypt operations." -ForegroundColor Yellow
}

# Encrypt / Decrypt options
Write-Host ""; Write-Host "Next actions:" -ForegroundColor Cyan
Write-Host "  1) Encrypt all .py files (will remove originals)"
Write-Host "  2) Decrypt all .encrypted.py files"
Write-Host "  3) Generate key again"
Write-Host "  4) Exit"

$choice = Read-Host "Choose an action (1-4)"
switch ($choice) {
    '1' {
        if (-not $env:ENCRYPTION_KEY) { Write-Warning "ENCRYPTION_KEY is not set. Aborting."; break }
        Write-Host "Encrypting all .py files (except bootstrap)..." -ForegroundColor Cyan
        python crypto_utils.py encrypt-all
    }
    '2' {
        if (-not $env:ENCRYPTION_KEY) { Write-Warning "ENCRYPTION_KEY is not set. Aborting."; break }
        Write-Host "Decrypting all .encrypted.py files..." -ForegroundColor Cyan
        python crypto_utils.py decrypt-all
    }
    '3' {
        Write-Host "Generating a new key..." -ForegroundColor Cyan
        python crypto_utils.py generate-key
    }
    default { Write-Host "Exiting." }
}

Write-Host "Done." -ForegroundColor Green
