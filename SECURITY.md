# Security Policy

## Overview

BaseForge is a local-only tool that performs encoding, decoding, hashing, and cryptographic operations entirely on your machine. It makes **no network requests** and **stores no data**.

## Security Features

- **Constant-time comparison**: HMAC verification uses `hmac.compare_digest()` to prevent timing attacks
- **No secrets logged**: The tool never prints, logs, or stores secret keys
- **No network calls**: All operations are performed locally
- **No persistent state**: No databases, no config files, no cached data
- **Input validation**: All inputs are validated before processing

## JWT Security Notes

- JWT validation only checks signature and expiration
- It does NOT verify the JWT was issued by a trusted party
- It does NOT check token audience claims by default
- For production use, always use a proper JWT library with full claim validation

## Hash Algorithm Recommendations

| Algorithm | Status | Use Case |
|-----------|--------|----------|
| MD5 | ⚠️ Deprecated | Non-security checksums only |
| SHA-1 | ⚠️ Deprecated | Legacy systems only |
| SHA-256 | ✅ Recommended | General purpose |
| SHA-3 | ✅ Recommended | High security requirements |
| BLAKE2 | ✅ Recommended | High performance |

## Known Limitations

- Caesar/Vigenere ciphers are educational only — not secure for real encryption
- Base64, Hex, etc. are encoding, NOT encryption — they provide no security
- JWT HMAC validation requires the secret — if the secret is compromised, the token is compromised

## Reporting Issues

If you discover a security vulnerability, please report it via GitHub Issues.
