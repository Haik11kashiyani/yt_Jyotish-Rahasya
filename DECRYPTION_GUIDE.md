# Decryption Guide - How to Update Encrypted Files

This document explains how to decrypt, update, and re-encrypt your Python files in this repository.

## Overview

All `.py` files in this repository are encrypted using `Fernet` encryption from the `cryptography` library. The encryption key is stored securely in GitHub Secrets.

- **Encrypted files**: `*.encrypted.py` (e.g., `main.encrypted.py`, `agents/astrologer.encrypted.py`)
- **Unencrypted files**: `crypto_utils.py`, `secure_bootstrap.py` (bootstrap for decryption)
- **Encryption key**: Stored in GitHub Secrets as `ENCRYPTION_KEY`

## When You Need to Decrypt Files

You need to decrypt files when:
1. You want to update code locally
2. You need to test changes before pushing
3. You want to review the decrypted source code

## Step 1: Set Up Environment Variable (Local Development)

The decryption requires your `ENCRYPTION_KEY` environment variable set.

### On Windows (PowerShell):
```powershell
$env:ENCRYPTION_KEY = "YOUR_ENCRYPTION_KEY_HERE"
```

### On Windows (Command Prompt):
```cmd
set ENCRYPTION_KEY=YOUR_ENCRYPTION_KEY_HERE
```

### On macOS/Linux:
```bash
export ENCRYPTION_KEY="YOUR_ENCRYPTION_KEY_HERE"
```

**Get your encryption key from:**
- GitHub: Settings → Secrets and variables → Actions → `ENCRYPTION_KEY`
- Save it securely (never commit it to the repository)

## Step 2: Decrypt All Files

Run this command in the repository root:

```bash
python crypto_utils.py decrypt-all
```

This will:
- Create decrypted `.py` files from all `.encrypted.py` files
- Leave the `.encrypted.py` files unchanged
- Replace any existing decrypted files

**Example output:**
```
Decrypting: agents/astrologer.encrypted.py → agents/astrologer.py
Decrypting: main.encrypted.py → main.py
...
Decryption complete!
```

## Step 3: Make Your Updates

Edit the decrypted `.py` files as needed:
```bash
code main.py
code agents/astrologer.py
# ... make your changes ...
```

## Step 4: Re-Encrypt Your Files

Once you've made changes, re-encrypt before pushing:

```bash
python crypto_utils.py encrypt-all
```

This will:
- Overwrite the `.encrypted.py` files with your updated code
- Leave the decrypted `.py` files in place
- You can delete the decrypted files afterward if desired

**Example output:**
```
Encrypting: main.py → main.encrypted.py
Encrypting: agents/astrologer.py → agents/astrologer.encrypted.py
...
Encryption complete!
```

## Step 5: Clean Up Decrypted Files (Recommended)

After re-encrypting, remove the decrypted versions locally:

```bash
python crypto_utils.py cleanup
```

Or manually:
```bash
# Remove all decrypted .py files (keep the .encrypted.py files)
rm main.py
rm agents/astrologer.py
rm agents/director.py
# ... etc ...
```

## Step 6: Commit and Push

```bash
git add .github/workflows/encrypt.yml
git add agents/*.encrypted.py
git add *.encrypted.py
git commit -m "Update encrypted files"
git push origin main
```

The GitHub Actions workflow will:
1. Detect the push
2. Commit the `.encrypted.py` files automatically
3. Skip re-encryption if files are already encrypted

## Workflow Automation

### Automatic Encryption on Push

The `encrypt.yml` workflow runs on every push and:
- Automatically encrypts any new `.py` files
- Commits the `.encrypted.py` versions
- Cleans up any decrypted files in the repo

### Decryption Verification

The `decrypt_verify.yml` workflow (manual trigger) will:
- Decrypt all encrypted files
- Verify Python syntax
- Ensure all files compile correctly
- Clean up decrypted files

**To run manually:**
1. Go to: Actions → Decrypt and Verify
2. Click "Run workflow"
3. Check the logs for any errors

## Important Notes

⚠️ **Security:**
- **Never** commit your `ENCRYPTION_KEY` to the repository
- **Never** commit decrypted `.py` files to the repository
- Keep your encryption key secure (GitHub Secrets, `.env` file locally)
- If your key is compromised, regenerate it and update GitHub Secrets

⚠️ **File Handling:**
- Only decrypt when needed
- Always re-encrypt before pushing to GitHub
- Use `cleanup` to remove decrypted files
- Use `.gitignore` to prevent accidental commits

## Troubleshooting

### "ENCRYPTION_KEY is not set"
**Solution:** Set the environment variable before running decrypt/encrypt commands

### "Decryption failed: Invalid token"
**Solution:** Your `ENCRYPTION_KEY` is incorrect or corrupted. Verify in GitHub Secrets.

### "No decrypted files found"
**Solution:** 
1. Ensure you ran `python crypto_utils.py decrypt-all`
2. Check that `crypto_utils.py` is in the repository root

### "Syntax error in decrypted file"
**Solution:** The file might be corrupted during encryption. Try:
1. Delete the `.py` file
2. Re-decrypt with `python crypto_utils.py decrypt-all`

## Quick Reference Commands

| Command | Purpose |
|---------|---------|
| `python crypto_utils.py decrypt-all` | Decrypt all `.encrypted.py` files |
| `python crypto_utils.py encrypt-all` | Encrypt all `.py` files → `.encrypted.py` |
| `python crypto_utils.py cleanup` | Remove all decrypted `.py` files |
| `python crypto_utils.py status` | Check encryption status |

## File Structure

```
repo/
├── .github/
│   └── workflows/
│       ├── encrypt.yml           # Auto-encrypts on push
│       ├── decrypt_verify.yml    # Manual verification
│       └── ... (production workflows with decryption)
├── crypto_utils.py               # Encryption/decryption tool (NEVER ENCRYPT)
├── secure_bootstrap.py           # Bootstrap code (NEVER ENCRYPT)
├── main.encrypted.py             # Encrypted main code
├── agents/
│   ├── astrologer.encrypted.py   # Encrypted agent
│   ├── director.encrypted.py     # Encrypted agent
│   └── ... (all other .encrypted.py files)
└── DECRYPTION_GUIDE.md           # This file
```

## Support

For issues or questions:
1. Check the GitHub Actions logs
2. Review this guide
3. Verify your `ENCRYPTION_KEY` is correct
4. Check that `cryptography` is installed: `pip install cryptography`
