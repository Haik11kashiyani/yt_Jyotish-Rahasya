# 🔐 Full-Project Encryption Setup Guide

This project uses **full-project encryption** to protect all Python source code. Only the bootstrap and encryption utilities remain unencrypted to enable decryption at runtime.

## Overview

```
Repository Files:
├── crypto_utils.py          ✅ UNENCRYPTED (bootstrap utility)
├── secure_bootstrap.py      ✅ UNENCRYPTED (bootstrap loader)
├── main.encrypted.py        🔒 ENCRYPTED
├── editor.encrypted.py      🔒 ENCRYPTED
├── generate_test_videos.encrypted.py  🔒 ENCRYPTED
├── agents/
│   ├── astrologer.encrypted.py       🔒 ENCRYPTED
│   ├── director.encrypted.py         🔒 ENCRYPTED
│   ├── narrator.encrypted.py         🔒 ENCRYPTED
│   ├── uploader.encrypted.py         🔒 ENCRYPTED
│   ├── stock_fetcher.encrypted.py    🔒 ENCRYPTED
│   ├── ephemeris.encrypted.py        🔒 ENCRYPTED
│   └── model_discovery.encrypted.py  🔒 ENCRYPTED
└── ... (all other .py files encrypted)
```

## Setup Steps

### 1️⃣ Generate Encryption Key

**On Linux/macOS:**
```bash
bash setup_encryption.sh
```

**On Windows:**
```cmd
setup_encryption.bat
```

This will:
- Generate a random Fernet encryption key
- Display the key (save it!)
- Show you where to add it to GitHub Secrets

### 2️⃣ Add ENCRYPTION_KEY to GitHub Secrets

1. Go to: https://github.com/Haik11kashiyani/yt_Jyotish-Rahasya/settings/secrets/actions
2. Click "New repository secret"
3. Set:
   - **Name:** `ENCRYPTION_KEY`
   - **Value:** (paste the key from step 1)
4. Click "Add secret"

**Or via GitHub CLI:**
```bash
gh secret set ENCRYPTION_KEY --body '<key-from-setup>'
```

### 3️⃣ Encrypt All Python Files (Local Setup)

Set your encryption key:
```bash
# Linux/macOS
export ENCRYPTION_KEY='<key-from-setup>'

# Windows
set ENCRYPTION_KEY=<key-from-setup>
```

Encrypt all files:
```bash
python crypto_utils.py encrypt-all
```

This will:
- Encrypt all `.py` files (except `crypto_utils.py` and `secure_bootstrap.py`)
- Create `.encrypted.py` versions
- Delete the original `.py` files
- Keep only encrypted versions in the repository

### 4️⃣ Commit Encrypted Files

```bash
git add -A
git commit -m "🔐 Encrypt project source code for security"
git push
```

## How It Works

### Runtime Decryption (CI/CD)

When a GitHub Actions workflow runs:

1. **Bootstrap phase** (unencrypted):
   - `crypto_utils.py` and `secure_bootstrap.py` load
   - Both read `ENCRYPTION_KEY` from GitHub Secrets

2. **Decryption phase**:
   ```yaml
   - name: 🔓 Decrypt All Modules
     env:
       ENCRYPTION_KEY: ${{ secrets.ENCRYPTION_KEY }}
     run: |
       python -c "
       from crypto_utils import ModuleEncryptor
       encryptor = ModuleEncryptor()
       encryptor.decrypt_all('.')
       "
   ```

3. **Execution phase**:
   - All `.py` files are now available in memory
   - The job runs normally with full functionality
   - No sensitive code is exposed in the repository

4. **Cleanup phase** (automatic):
   ```yaml
   - name: 🧹 Cleanup Decrypted Files
     if: always()
     run: |
       python -c "
       from crypto_utils import cleanup_decrypted_files
       cleanup_decrypted_files('.')
       "
   ```
   - All decrypted files are permanently deleted
   - Only encrypted versions remain

### Local Development

To work locally with the encrypted code:

**Decrypt all files:**
```bash
export ENCRYPTION_KEY='<your-key>'
python crypto_utils.py decrypt-all
```

**Or decrypt a specific file:**
```bash
export ENCRYPTION_KEY='<your-key>'
python crypto_utils.py decrypt agents/astrologer.encrypted.py
```

After editing, re-encrypt:
```bash
export ENCRYPTION_KEY='<your-key>'
python crypto_utils.py encrypt-all
```

## Encryption/Decryption Commands

### Generate a new key:
```bash
python crypto_utils.py generate-key
```

### Encrypt all Python files:
```bash
export ENCRYPTION_KEY='<your-key>'
python crypto_utils.py encrypt-all
```

### Decrypt all encrypted files:
```bash
export ENCRYPTION_KEY='<your-key>'
python crypto_utils.py decrypt-all
```

### Encrypt a single file:
```bash
export ENCRYPTION_KEY='<your-key>'
python crypto_utils.py encrypt <file.py>
```

### Decrypt a single file:
```bash
export ENCRYPTION_KEY='<your-key>'
python crypto_utils.py decrypt <file.encrypted.py>
```

## Security Benefits

✅ **Source code never exposed in repository** - Only encrypted `.encrypted.py` files are stored  
✅ **Single secret management** - Only `ENCRYPTION_KEY` needed (no individual API key exposure)  
✅ **Zero local secrets** - Code is encrypted at rest in the repository  
✅ **Runtime-only decryption** - Code only exists in memory during execution  
✅ **Automatic cleanup** - No decrypted files left on CI/CD runners  
✅ **Minimal bootstrap** - Only `crypto_utils.py` and `secure_bootstrap.py` needed to unlock everything  

## Bootstrap Files (Always Unencrypted)

These files are **intentionally unencrypted** because they're needed to decrypt other modules:

| File | Why Unencrypted |
|------|-----------------|
| `crypto_utils.py` | Contains the decryption logic (chicken-and-egg problem) |
| `secure_bootstrap.py` | Initializes the decryption system at runtime |

These files contain **no sensitive information** - they're pure utilities.

## Troubleshooting

### "ENCRYPTION_KEY not set" error

**Solution:** Add `ENCRYPTION_KEY` to GitHub Secrets (see Step 2 above)

### "Decryption failed (invalid key?)" error

**Solution:** Ensure the key in GitHub Secrets matches the key used to encrypt files

### Can't import modules locally

**Solution:** 
1. Make sure you have the correct `ENCRYPTION_KEY` set
2. Run `python crypto_utils.py decrypt-all` to decrypt files
3. Try importing again

### Need to update encrypted files

1. Decrypt: `python crypto_utils.py decrypt-all`
2. Edit the `.py` files
3. Re-encrypt: `python crypto_utils.py encrypt-all`
4. Commit encrypted versions

## API Keys & Secrets Strategy

**Before:** API keys hardcoded or in `.env` → exposed if repo is compromised
**Now:** 
- All code is encrypted in the repository
- API keys are passed via GitHub Secrets environment variables
- `ENCRYPTION_KEY` is the only repository secret
- Individual API keys can stay in `secure_bootstrap.py` or be passed as env vars

```python
# secure_bootstrap.py (unencrypted utility, no secrets)
import os
api_key = os.getenv("OPENROUTER_API_KEY")  # From GitHub Secrets

# agents/astrologer.encrypted.py (encrypted - safe in repo)
# Uses os.getenv() to access keys at runtime
```

## Workflow Example

```yaml
jobs:
  produce-video:
    runs-on: ubuntu-latest
    steps:
      # ... setup steps ...

      - name: 🔓 Decrypt All Modules
        env:
          ENCRYPTION_KEY: ${{ secrets.ENCRYPTION_KEY }}
        run: python -c "from crypto_utils import ModuleEncryptor; ModuleEncryptor().decrypt_all('.')"

      - name: Run Production Studio
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
          YOUTUBE_CLIENT_ID: ${{ secrets.YOUTUBE_CLIENT_ID }}
          YOUTUBE_CLIENT_SECRET: ${{ secrets.YOUTUBE_CLIENT_SECRET }}
          YOUTUBE_REFRESH_TOKEN: ${{ secrets.YOUTUBE_REFRESH_TOKEN }}
        run: python main.py --rashi "Mesh (Aries)" --type shorts --upload

      - name: 🧹 Cleanup Decrypted Files
        if: always()
        run: python -c "from crypto_utils import cleanup_decrypted_files; cleanup_decrypted_files('.')"
```

## Files Encrypted in This Project

**Root directory (8 files):**
- `main.py` → `main.encrypted.py`
- `editor.py` → `editor.encrypted.py`
- `generate_test_videos.py` → `generate_test_videos.encrypted.py`
- `check_anims.py` → `check_anims.encrypted.py`
- `create_icon.py` → `create_icon.encrypted.py`
- `debug_imports.py` → `debug_imports.encrypted.py`
- `get_youtube_token.py` → `get_youtube_token.encrypted.py`
- `get_refresh_token.py` → `get_refresh_token.encrypted.py`

**agents/ directory (7 files):**
- `astrologer.py` → `astrologer.encrypted.py`
- `director.py` → `director.encrypted.py`
- `narrator.py` → `narrator.encrypted.py`
- `uploader.py` → `uploader.encrypted.py`
- `stock_fetcher.py` → `stock_fetcher.encrypted.py`
- `ephemeris.py` → `ephemeris.encrypted.py`
- `model_discovery.py` → `model_discovery.encrypted.py`

**Total: 15 files encrypted**

## Questions?

See the inline documentation in:
- `crypto_utils.py` - Encryption/decryption implementation
- `secure_bootstrap.py` - Bootstrap loading mechanism
- Workflow files in `.github/workflows/` - Runtime decryption flow
