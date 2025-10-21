# Webhook Integration Guide

## What are Webhooks?

Webhooks allow you to receive real-time notifications when events occur in your account. Instead of polling our API, we'll send HTTP POST requests to your specified endpoint.

## Setting Up Webhooks

### Creating a Webhook Endpoint

1. Log into your dashboard
2. Go to Settings > Webhooks
3. Click "Add Endpoint"
4. Enter your webhook URL (must be HTTPS)
5. Select the events you want to receive
6. Click "Create Endpoint"
7. Copy the signing secret for verification

### Webhook URL Requirements

Your webhook endpoint must:
- Use HTTPS (HTTP not supported in production)
- Respond within 5 seconds
- Return a 2xx HTTP status code
- Be publicly accessible
- Handle duplicate events idempotently

## Available Events

### User Events
- `user.created` - New user registered
- `user.updated` - User information changed
- `user.deleted` - User account deleted

### Billing Events
- `invoice.created` - New invoice generated
- `invoice.paid` - Invoice payment successful
- `invoice.payment_failed` - Invoice payment failed
- `subscription.created` - New subscription started
- `subscription.updated` - Subscription plan changed
- `subscription.canceled` - Subscription canceled

### System Events
- `api_key.created` - New API key generated
- `api_key.revoked` - API key revoked
- `account.suspended` - Account suspended
- `account.reactivated` - Account reactivated

## Webhook Payload Format

All webhook events follow this structure:

```json
{
  "id": "evt_1234567890",
  "type": "invoice.paid",
  "created": 1640995200,
  "data": {
    "object": {
      "id": "inv_abc123",
      "amount": 9900,
      "currency": "usd",
      "status": "paid",
      "customer": {
        "id": "cus_xyz789",
        "email": "customer@example.com"
      }
    }
  },
  "api_version": "v1"
}
```

## Verifying Webhook Signatures

**Always verify webhook signatures** to ensure the request came from us.

### Signature Header

We include a signature in the `X-Webhook-Signature` header:
```
X-Webhook-Signature: t=1640995200,v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd
```

### Verification Steps

1. Extract timestamp and signature from header
2. Create signature payload: `{timestamp}.{raw_request_body}`
3. Compute HMAC with SHA256 using your signing secret
4. Compare computed signature with received signature
5. Check timestamp to prevent replay attacks (tolerance: 5 minutes)

### Example Verification (Python)

```python
import hmac
import hashlib
import time

def verify_webhook_signature(payload, signature_header, signing_secret):
    # Parse signature header
    elements = signature_header.split(',')
    timestamp = int(elements[0].split('=')[1])
    signature = elements[1].split('=')[1]
    
    # Check timestamp (prevent replay attacks)
    current_time = int(time.time())
    if abs(current_time - timestamp) > 300:  # 5 minutes
        raise ValueError("Timestamp too old")
    
    # Compute expected signature
    signed_payload = f"{timestamp}.{payload}"
    expected_signature = hmac.new(
        signing_secret.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Secure comparison
    if not hmac.compare_digest(expected_signature, signature):
        raise ValueError("Invalid signature")
    
    return True
```

### Example Verification (Node.js)

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signatureHeader, signingSecret) {
  const [tPart, vPart] = signatureHeader.split(',');
  const timestamp = parseInt(tPart.split('=')[1]);
  const signature = vPart.split('=')[1];
  
  // Check timestamp
  const currentTime = Math.floor(Date.now() / 1000);
  if (Math.abs(currentTime - timestamp) > 300) {
    throw new Error('Timestamp too old');
  }
  
  // Compute expected signature
  const signedPayload = `${timestamp}.${payload}`;
  const expectedSignature = crypto
    .createHmac('sha256', signingSecret)
    .update(signedPayload)
    .digest('hex');
  
  // Secure comparison
  if (!crypto.timingSafeEqual(
    Buffer.from(expectedSignature),
    Buffer.from(signature)
  )) {
    throw new Error('Invalid signature');
  }
  
  return true;
}
```

## Handling Webhooks

### Best Practices

1. **Respond quickly** - Acknowledge receipt immediately
2. **Process asynchronously** - Queue events for background processing
3. **Handle duplicates** - Store event IDs and skip duplicates
4. **Retry logic** - Implement exponential backoff for failed processing
5. **Log everything** - Keep detailed logs for debugging

### Example Handler (Express.js)

```javascript
const express = require('express');
const app = express();

app.post('/webhooks', express.raw({type: 'application/json'}), (req, res) => {
  const signature = req.headers['x-webhook-signature'];
  const payload = req.body;
  
  try {
    // Verify signature
    verifyWebhookSignature(payload, signature, SIGNING_SECRET);
    
    // Parse event
    const event = JSON.parse(payload);
    
    // Queue for background processing
    jobQueue.add('process-webhook', event);
    
    // Respond immediately
    res.status(200).json({received: true});
    
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(400).json({error: error.message});
  }
});
```

## Retry Logic

If your endpoint fails to respond or returns an error:

1. **Immediate retry** - If initial request fails
2. **Retry after 1 minute**
3. **Retry after 5 minutes**
4. **Retry after 30 minutes**
5. **Retry after 2 hours**
6. **Final retry after 6 hours**

After all retries fail, the event is marked as failed. You can manually replay failed events from the dashboard.

## Testing Webhooks

### Using Webhook Testing Tools

- **ngrok**: Expose local server to internet
  ```bash
  ngrok http 3000
  ```
  
- **webhook.site**: Test endpoint for development

### Test Mode

Enable test mode in your dashboard to:
- Send test events manually
- View webhook delivery logs
- Replay recent events
- Debug signature verification

### Manual Testing

Send a test event from the dashboard:
1. Go to Settings > Webhooks
2. Click on your endpoint
3. Click "Send Test Event"
4. Select event type
5. View delivery status and response

## Monitoring Webhooks

### Webhook Dashboard

Monitor webhook health:
- Delivery success rate
- Average response time
- Recent failures
- Event timeline

### Alerts

Set up alerts for:
- Delivery failure rate > 10%
- Endpoint response time > 3 seconds
- Signature verification failures

## Troubleshooting

### Webhooks Not Being Received

1. ✓ Endpoint URL is correct and publicly accessible
2. ✓ Using HTTPS (required in production)
3. ✓ Firewall/security groups allow inbound traffic
4. ✓ Server is running and responding
5. ✓ Check webhook logs in dashboard for errors

### Signature Verification Failing

1. ✓ Using correct signing secret
2. ✓ Verifying raw request body (not parsed JSON)
3. ✓ Timestamp validation is not too strict
4. ✓ Server time is synchronized

### Timeouts

If webhooks are timing out:
- Respond immediately (200 OK)
- Process events asynchronously
- Don't make external API calls in webhook handler
- Optimize database queries

## Security Considerations

- Always verify webhook signatures
- Use HTTPS for webhook endpoints
- Validate event data before processing
- Implement rate limiting on webhook endpoints
- Log all webhook activity
- Rotate signing secrets periodically

## Getting Help

- Webhook Documentation: https://docs.company.com/webhooks
- Test your webhooks: Settings > Webhooks > Test
- Support: webhooks-support@company.com

