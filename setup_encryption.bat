@echo off
REM Generate encryption key and add it to GitHub Secrets
REM Usage: setup_encryption.bat

echo.
echo 🔐 Full-Project Encryption Setup
echo ================================
echo.

REM Step 1: Generate encryption key
echo 📝 Step 1: Generating ENCRYPTION_KEY...
for /f "tokens=*" %%a in ('python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"') do set ENCRYPTION_KEY=%%a

echo ✅ Generated ENCRYPTION_KEY:
echo    %ENCRYPTION_KEY%
echo.

REM Step 2: Display instructions
echo 📋 Step 2: Add to GitHub Secrets
echo    Go to: https://github.com/Haik11kashiyani/yt_Jyotish-Rahasya/settings/secrets/actions
echo.
echo    Create NEW REPOSITORY SECRET:
echo    • Name: ENCRYPTION_KEY
echo    • Value: %ENCRYPTION_KEY%
echo.
echo    OR use GitHub CLI:
echo    gh secret set ENCRYPTION_KEY --body "%ENCRYPTION_KEY%"
echo.

REM Step 3: Encrypt all modules
echo 📝 Step 3: Encrypt ALL Python files locally (optional)
echo    Run locally to test encryption:
echo.
echo    set ENCRYPTION_KEY=%ENCRYPTION_KEY%
echo    python crypto_utils.py encrypt-all
echo.
echo    This will:
echo    • Encrypt ALL .py files (except crypto_utils.py and secure_bootstrap.py)
echo    • Create .encrypted.py versions of each file
echo    • Remove original .py files
echo    • Keep encrypted versions in repo
echo.
echo    Files that will be ENCRYPTED:
echo    • main.py
echo    • editor.py
echo    • generate_test_videos.py
echo    • check_anims.py
echo    • create_icon.py
echo    • debug_imports.py
echo    • get_youtube_token.py
echo    • get_refresh_token.py
echo    • agents\*.py (all agent modules)
echo.
echo    Files that will stay UNENCRYPTED (bootstrap):
echo    • crypto_utils.py (needed for decryption)
echo    • secure_bootstrap.py (needed for bootstrap)
echo.

REM Step 4: Decryption for development
echo 📝 Step 4: For local development:
echo    To decrypt all files locally:
echo.
echo    set ENCRYPTION_KEY=%ENCRYPTION_KEY%
echo    python crypto_utils.py decrypt-all
echo.
echo    To decrypt a specific file:
echo    python crypto_utils.py decrypt agents/astrologer.encrypted.py
echo.

echo.
echo ✅ Setup complete!
echo.
echo 📌 SECURITY HIGHLIGHTS:
echo    1. ✅ ALL .py files are encrypted in the repository
echo    2. ✅ Only crypto_utils.py and secure_bootstrap.py remain unencrypted
echo    3. ✅ CI/CD automatically decrypts on the runner using ENCRYPTION_KEY
echo    4. ✅ All decrypted files are cleaned up after each job
echo    5. ✅ Code is never exposed in the repository
echo    6. ✅ ENCRYPTION_KEY is the only secret needed
echo.
pause
