# SSL Certificate Generation for Development
# For production, use Let's Encrypt with certbot

# This script generates self-signed certificates for local development/testing.
# DO NOT use self-signed certs in production!

Write-Host "Generating self-signed SSL certificates for development..."

$sslPath = "nginx\ssl"

# Check if OpenSSL is available
try {
    $opensslVersion = openssl version
    Write-Host "Using OpenSSL: $opensslVersion"
}
catch {
    Write-Host "ERROR: OpenSSL not found. Please install OpenSSL or use WSL."
    Write-Host "  Windows: choco install openssl"
    Write-Host "  Or use: https://slproweb.com/products/Win32OpenSSL.html"
    exit 1
}

# Generate private key and certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
    -keyout "$sslPath\key.pem" `
    -out "$sslPath\cert.pem" `
    -subj "/C=ID/ST=Jakarta/L=Jakarta/O=MicroLLM/OU=PrivateStack/CN=localhost"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS! SSL certificates generated:"
    Write-Host "  Certificate: $sslPath\cert.pem"
    Write-Host "  Private Key: $sslPath\key.pem"
    Write-Host ""
    Write-Host "WARNING: These are self-signed certificates for DEVELOPMENT ONLY."
    Write-Host "For production, use Let's Encrypt:"
    Write-Host "  docker run -it --rm -v ./nginx/ssl:/etc/letsencrypt certbot/certbot certonly"
}
else {
    Write-Host "ERROR: Failed to generate certificates"
}
