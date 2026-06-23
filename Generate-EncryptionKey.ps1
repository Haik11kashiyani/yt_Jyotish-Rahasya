# PowerShell script to generate Fernet encryption key
# This doesn't require Python - generates base64 key natively

# Generate 32 random bytes (256 bits) for Fernet key
$randomBytes = [byte[]]::new(32)
$rng = [System.Security.Cryptography.RNGCryptoServiceProvider]::new()
$rng.GetBytes($randomBytes)

# Add Fernet version byte (0x80 = version 128)
$versionByte = [byte]0x80
$keyBytes = @($versionByte) + $randomBytes

# Generate timestamp (64-bit current Unix timestamp)
$unixTime = [Math]::Floor([datetime]::UtcNow.Subtract([datetime]'1970-01-01').TotalSeconds)
$timeByte1 = [byte](($unixTime -shr 56) -band 0xFF)
$timeByte2 = [byte](($unixTime -shr 48) -band 0xFF)
$timeByte3 = [byte](($unixTime -shr 40) -band 0xFF)
$timeByte4 = [byte](($unixTime -shr 32) -band 0xFF)
$timeByte5 = [byte](($unixTime -shr 24) -band 0xFF)
$timeByte6 = [byte](($unixTime -shr 16) -band 0xFF)
$timeByte7 = [byte](($unixTime -shr 8) -band 0xFF)
$timeByte8 = [byte]($unixTime -band 0xFF)

$timeBytes = @($timeByte1, $timeByte2, $timeByte3, $timeByte4, $timeByte5, $timeByte6, $timeByte7, $timeByte8)

# Generate HMAC signature (using SHA256, take first 16 bytes)
$keyMaterial = $keyBytes + $timeBytes
$hmac = [System.Security.Cryptography.HMACSHA256]::new($keyBytes)
$signature = $hmac.ComputeHash($keyMaterial)
$signatureShort = $signature[0..15]

# Combine all parts
$finalKey = $keyBytes + $timeBytes + $signatureShort

# Encode to Base64
$encodedKey = [Convert]::ToBase64String($finalKey)

Write-Host ""
Write-Host "ENCRYPTION_KEY Generated Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your new ENCRYPTION_KEY:" -ForegroundColor Yellow
Write-Host $encodedKey -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Copy the key above (Ctrl+C)" -ForegroundColor White
Write-Host ""
Write-Host "2. Add to GitHub Secrets:" -ForegroundColor White
Write-Host "   https://github.com/Haik11kashiyani/yt_Jyotish-Rahasya/settings/secrets/actions" -ForegroundColor White
Write-Host "   - Click New repository secret" -ForegroundColor White
Write-Host "   - Name: ENCRYPTION_KEY" -ForegroundColor White
Write-Host "   - Value: paste the key from above" -ForegroundColor White
Write-Host ""
Write-Host "3. Encrypt all Python files:" -ForegroundColor White
Write-Host '   Set-Item -Path env:ENCRYPTION_KEY -Value "YOUR_KEY"' -ForegroundColor Cyan
Write-Host "   python crypto_utils.py encrypt-all" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Commit and push:" -ForegroundColor White
Write-Host "   git add -A" -ForegroundColor Cyan
Write-Host "   git commit -m \"Full-project encryption\"" -ForegroundColor Cyan
Write-Host "   git push" -ForegroundColor Cyan
Write-Host ""
