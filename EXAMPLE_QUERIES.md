# Example Queries for Testing

This document provides example queries to test each specialized agent and demonstrate the different retrieval strategies.

## Billing Support Agent (Hybrid RAG/CAG)

The Billing Agent uses a **Hybrid RAG/CAG strategy**: first query performs RAG retrieval, subsequent queries in the same session use cached context for faster responses.

### Pricing Questions
```
"What are your pricing plans?"
"How much does the Enterprise plan cost?"
"What features are included in the Professional plan?"
"What's the difference between Starter and Professional plans?"
"Do you offer volume discounts?"
```

### Invoice Questions
```
"How can I view my invoices?"
"When will I receive my invoice?"
"What payment methods do you accept?"
"Can I get a refund for my subscription?"
"How do I download past invoices?"
```

### Subscription Management
```
"How do I upgrade my subscription?"
"Can I downgrade my plan mid-month?"
"What happens if my payment fails?"
"How do I cancel my subscription?"
"Do you offer annual billing?"
```

### Payment Methods
```
"Can I pay with PayPal?"
"How do I add a credit card?"
"Do you accept wire transfers?"
"Can I use ACH for payments?"
"How do I update my payment method?"
```

---

## Technical Support Agent (Pure RAG)

The Technical Agent uses **Pure RAG strategy**: every query performs a fresh vector similarity search to retrieve the most relevant technical documentation.

### Account & Authentication
```
"How do I reset my password?"
"I forgot my password, what should I do?"
"How do I enable two-factor authentication?"
"My account is locked, how do I unlock it?"
"How do I change my email address?"
```

### API Integration
```
"How do I authenticate with your API?"
"My API authentication is failing, what should I do?"
"What's causing a 401 error in the API?"
"How do I get an API key?"
"What are the API rate limits?"
```

### Webhooks
```
"How do I set up webhooks?"
"My webhooks aren't working, how do I debug them?"
"How do I verify webhook signatures?"
"What events can I subscribe to with webhooks?"
"Why am I not receiving webhook notifications?"
```

### Common Errors
```
"I'm getting a 429 error, what does it mean?"
"How do I fix 'Invalid credentials' error?"
"What causes a 'Session expired' error?"
"How do I resolve 'Rate limit exceeded'?"
"My file upload is failing, what should I check?"
```

### Account Setup
```
"How do I create an account?"
"What are the steps to set up my profile?"
"How do I invite team members?"
"How do I configure integrations?"
"What are the security best practices?"
```

---

## Policy & Compliance Agent (Pure CAG)

The Policy Agent uses **Pure CAG strategy**: all policy documents are loaded into memory at startup for instant, consistent responses without per-query vector searches.

### Privacy & Data Protection
```
"What is your privacy policy?"
"How do you handle user data?"
"Where is my data stored?"
"Can I export my data?"
"How long do you retain my data?"
```

### GDPR Compliance
```
"Are you GDPR compliant?"
"What rights do I have under GDPR?"
"How do I request data deletion?"
"Can I access all my personal data?"
"How do you handle data transfers?"
```

### Terms of Service
```
"What are your terms of service?"
"What are the acceptable use policies?"
"Can I use this for commercial purposes?"
"What happens if I violate the terms?"
"How do I terminate my account?"
```

### Data Retention
```
"What is your data retention policy?"
"How long do you keep deleted data?"
"When are backups deleted?"
"What data is retained after account closure?"
"How do you handle data breaches?"
```

### Legal & Compliance
```
"Do you have SOC 2 certification?"
"Are you HIPAA compliant?"
"What security measures do you have?"
"How do you handle legal requests for data?"
"What's your refund policy?"
```

---

## Multi-Turn Conversations

Test conversation continuity with follow-up questions:

### Billing Conversation
```
User: "What are your pricing plans?"
AI: [Explains pricing plans]
User: "What about the Enterprise plan specifically?"
AI: [Details Enterprise plan using cached context - CAG]
User: "How do I upgrade to Enterprise?"
AI: [Explains upgrade process using cached context - CAG]
```

### Technical Conversation
```
User: "How do I reset my password?"
AI: [Provides password reset steps]
User: "I'm not receiving the reset email"
AI: [Troubleshoots email issues - new RAG query]
User: "Where should I check for the email?"
AI: [Provides additional guidance - new RAG query]
```

### Policy Conversation
```
User: "What's your privacy policy?"
AI: [Explains privacy policy from memory - CAG]
User: "Are you GDPR compliant?"
AI: [Explains GDPR compliance from memory - CAG]
User: "How do I request my data?"
AI: [Explains data request process from memory - CAG]
```

---

## Testing Routing Accuracy

These queries test the orchestrator's ability to route to the correct agent:

### Edge Cases
```
"How much does it cost and what's your privacy policy?"
→ Should route to Billing (first question priority)

"I can't access my account and need to see my invoice"
→ Should route to Technical (authentication issue is primary)

"What are the terms for API usage?"
→ Should route to Policy (terms of service question)

"My API key isn't working and I'm getting billed incorrectly"
→ Could route to either Technical or Billing (ambiguous)
```

---

## Performance Testing

### Test Hybrid RAG/CAG (Billing Agent)
1. Ask: "What are your pricing plans?" (Initial RAG query - slower)
2. Ask: "What's in the Professional plan?" (Uses cache - faster)
3. Ask: "How about Enterprise?" (Uses cache - faster)

**Expected**: First query takes longer, subsequent queries are faster using cached context.

### Test Pure RAG (Technical Agent)
1. Ask: "How do I reset my password?"
2. Ask: "How do I setup webhooks?"
3. Ask: "What API errors might I encounter?"

**Expected**: Each query performs vector search, retrieval time similar for all.

### Test Pure CAG (Policy Agent)
1. Ask: "What's your privacy policy?"
2. Ask: "Are you GDPR compliant?"
3. Ask: "What's your data retention policy?"

**Expected**: All queries respond instantly using pre-loaded documents, no retrieval delay.

---

## Video Demonstration Queries

For your YouTube video demonstration, use these queries to showcase all features:

1. **Introduction & Routing**
   - "What are your pricing plans?" → Shows Billing Agent
   - "How do I reset my password?" → Shows Technical Agent
   - "What's your privacy policy?" → Shows Policy Agent

2. **Detailed Agent Showcase**
   - Billing: "What's included in the Enterprise plan?" → Shows Hybrid RAG/CAG
   - Technical: "How do I set up webhooks?" → Shows Pure RAG with sources
   - Policy: "Am I protected under GDPR?" → Shows Pure CAG instant response

3. **Conversation Flow**
   - Multi-turn conversation demonstrating context maintenance
   - Show streaming responses in real-time
   - Demonstrate session management

4. **Architecture Walkthrough**
   - Explain the orchestrator routing decision
   - Show different retrieval strategies in action
   - Highlight OpenAI (workers) vs Bedrock (orchestrator) usage

---

## Notes for Testing

- **Session Persistence**: Conversations are maintained within a session
- **Streaming**: Watch responses stream in real-time for better UX
- **Error Handling**: Try invalid queries to test error responses
- **Rate Limiting**: Excessive requests may hit API rate limits
- **Routing**: The orchestrator uses Bedrock Claude for fast, cost-effective routing
- **Sources**: Technical agent includes source citations from retrieved documents

