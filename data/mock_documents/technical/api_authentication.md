# API Authentication Guide

## Overview

Our API uses token-based authentication. All API requests must include a valid API key in the request headers.

## Getting Your API Key

### Creating an API Key

1. Log into your account dashboard
2. Navigate to Settings > API Keys
3. Click "Generate New API Key"
4. Enter a name for the key (e.g., "Production", "Development")
5. Select permissions/scopes for the key
6. Click "Generate"
7. **Copy the key immediately** - it will only be shown once!

### API Key Scopes

Available permission scopes:
- `read`: Read-only access to all resources
- `write`: Create and update resources
- `delete`: Delete resources
- `admin`: Full administrative access

Best practice: Use the minimum required scope for each key.

## Making Authenticated Requests

### Using API Keys

Include your API key in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.company.com/v1/users
```

### Request Headers

Required headers:
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

Optional but recommended:
```
User-Agent: YourApp/1.0
Accept: application/json
```

## Common Authentication Errors

### 401 Unauthorized

**Cause:** Missing or invalid API key

**Solutions:**
- Verify your API key is included in the Authorization header
- Check for typos in the key
- Ensure you're using "Bearer" prefix
- Verify the key hasn't been revoked or expired

Example error response:
```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing API key",
  "status": 401
}
```

### 403 Forbidden

**Cause:** Valid API key but insufficient permissions

**Solutions:**
- Check the required scope for the endpoint
- Generate a new API key with appropriate permissions
- Verify your plan includes access to this endpoint

Example error response:
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions for this operation",
  "required_scope": "write",
  "your_scope": "read",
  "status": 403
}
```

### 429 Too Many Requests

**Cause:** Rate limit exceeded

**Solutions:**
- Implement exponential backoff
- Check your plan's rate limits
- Upgrade your plan for higher limits
- Cache responses when possible

Example error response:
```json
{
  "error": "Rate Limit Exceeded",
  "message": "Too many requests",
  "retry_after": 60,
  "limit": 1000,
  "status": 429
}
```

## Rate Limits

Rate limits by plan:
- **Starter**: 1,000 requests/day
- **Professional**: 10,000 requests/day
- **Enterprise**: Unlimited (fair use policy applies)

Rate limit headers included in all responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 997
X-RateLimit-Reset: 1640995200
```

## Best Practices

### Security
- **Never expose API keys in client-side code**
- Store keys in environment variables
- Rotate keys regularly (every 90 days recommended)
- Use different keys for development and production
- Revoke unused keys immediately

### Error Handling
```python
import requests

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(
        "https://api.company.com/v1/users",
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
except requests.exceptions.HTTPError as e:
    if response.status_code == 401:
        print("Authentication failed - check your API key")
    elif response.status_code == 429:
        print(f"Rate limit exceeded - retry after {response.headers.get('Retry-After')} seconds")
    else:
        print(f"HTTP error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

### Rate Limit Management
- Implement exponential backoff
- Monitor X-RateLimit-Remaining header
- Cache responses when appropriate
- Use webhooks instead of polling

## OAuth 2.0 (Enterprise Only)

Enterprise customers can use OAuth 2.0 for user-delegated access:

1. Register your OAuth application
2. Implement the OAuth flow
3. Exchange authorization code for access token
4. Use refresh tokens to maintain access

See full OAuth documentation at: https://docs.company.com/oauth

## Troubleshooting Checklist

If API requests are failing:

1. ✓ API key is correct and not expired
2. ✓ Using correct Authorization header format
3. ✓ API key has required permissions/scopes
4. ✓ Not exceeding rate limits
5. ✓ Using correct API endpoint URL
6. ✓ Request payload is valid JSON
7. ✓ Network/firewall not blocking requests
8. ✓ Server time is synchronized (for OAuth)

## Getting Help

- API Documentation: https://docs.company.com/api
- Status Page: https://status.company.com
- Support: api-support@company.com
- Community Forum: https://community.company.com

