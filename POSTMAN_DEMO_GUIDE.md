# Postman Demo Guide - Early Intervention GenAI API

## 🚀 Quick Setup

1. **Import Collection**: Open Postman → Import → Select `EI_GenAI_Postman_Collection.json`
2. **Server Running**: Ensure server is running on `http://localhost:8081`
3. **Ready to Demo**: All requests are pre-configured!

---

## 📋 Demo Flow (Recommended Order)

### **1. API Info** 
**Request:** GET `/`
- Shows API version and available endpoints
- Good intro to show what's available

### **2. Generate Intervention Plan - Communication (24mo)**
**Request:** POST `/api/plan`
```json
{
  "age_months": 24,
  "domain": "communication",
  "extra_info": "struggles with two-word combinations and following simple directions"
}
```
**Highlights:**
- ✅ Age-appropriate goals
- ✅ Evidence-based strategies from KIManual
- ✅ Practical parent advice
- ✅ JSON structured response

### **3. Generate Intervention Plan - Fine Motor (18mo)**
**Request:** POST `/api/plan`
```json
{
  "age_months": 18,
  "domain": "fine_motor",
  "extra_info": "difficulty with pincer grasp and stacking blocks"
}
```
**Highlights:**
- Shows different domain support
- Age-specific recommendations

### **4. Chat - New Session**
**Request:** POST `/api/chat`
```json
{
  "message": "How can I help my 18-month-old learn to follow simple directions?",
  "age_months": 18,
  "domain": "communication"
}
```
**Important:** 
- **Copy the `session_id`** from the response!
- You'll need it for the next request

**Highlights:**
- ✅ Conversational responses
- ✅ References FGRBI manual concepts
- ✅ Practical, parent-friendly advice

### **5. Chat - Continue Session**
**Request:** POST `/api/chat`
```json
{
  "message": "What about during mealtime specifically?",
  "session_id": "PASTE_SESSION_ID_HERE"
}
```
**Important:** Replace `PASTE_SESSION_ID_HERE` with actual session_id from step 4

**Highlights:**
- ✅ Maintains conversation context
- ✅ Builds on previous discussion
- ✅ Shows session memory working

---

## 🎯 Key Demo Points to Emphasize

### **RAG in Action**
- All responses grounded in KIManual2025 (286K chars, 106 pages)
- Model references specific strategies: "embedded instructional strategies", "FGRBI manual", etc.
- Age and domain-aware context retrieval

### **Structured Output**
- Plan endpoint returns strict JSON: `Goals`, `Strategies`, `Advice for Parents`
- Consistent format for integration with frontend/apps

### **Session Management**
- Chat maintains conversation history (last 12 messages)
- UUID-based sessions
- Seamless multi-turn conversations

### **Flexible Input**
- Supports both JSON and form-data
- Optional parameters (session_id, age_months, domain in chat)
- Validation with helpful error messages

---

## 💡 Additional Demo Scenarios

### **Scenario 1: Different Age Groups**
Show how responses adapt:
- **12 months** - Early communication/motor skills
- **24 months** - Word combinations, parallel play
- **36 months** - Complex sentences, peer interaction

### **Scenario 2: Different Domains**
- `communication` - Language, following directions
- `fine_motor` - Hand skills, self-feeding
- `gross_motor` - Walking, climbing, balance
- `social` - Peer interaction, sharing
- `cognitive` - Problem-solving, symbolic play
- `adaptive` - Self-care, routines

### **Scenario 3: Chat Without Age/Domain**
```json
{
  "message": "What are general tips for supporting my toddler's development?"
}
```
- Shows system works even without specific context
- Still provides evidence-based advice

---

## 🔧 Troubleshooting

**Error: "Connection refused"**
- Check server is running: `uvicorn app.main:app --reload --port 8081`

**Error: "Groq API error"**
- Check `.env` has valid `GROQ_API_KEY`
- Verify model: `llama-3.1-8b-instant`

**Error: "session_id not found"**
- Sessions are in-memory (cleared on restart)
- Generate new session by sending chat without session_id

---

## 📊 Expected Response Times

- **Plan Generation**: 3-8 seconds
- **Chat Response**: 2-5 seconds
- **KB Upload**: <1 second
- **Root Endpoint**: <100ms

---

## 🎬 Demo Script Example

**Opening:**
> "This is our Early Intervention GenAI API that helps therapists and parents create personalized intervention plans using AI powered by our 106-page KI Manual."

**Demo Plan Generation:**
> "Let me show you generating a plan for a 24-month-old with communication delays..."
> [Run request]
> "Notice how it provides specific, measurable goals, evidence-based strategies, and practical advice for parents—all grounded in our knowledge base."

**Demo Chat:**
> "Now let's show the conversational interface..."
> [Run first chat]
> "The system references specific strategies from our FGRBI manual. Let me ask a follow-up..."
> [Run second chat with session_id]
> "See how it maintains context and builds on the previous answer? That's the session memory in action."

**Closing:**
> "The system supports all developmental domains, ages 0-36 months, and can handle both structured plan generation and conversational support—all backed by evidence from our knowledge base."

---

## 📝 Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API info |
| `/api/rag/upload` | POST | Upload knowledge base |
| `/api/plan` | POST | Generate intervention plan |
| `/api/chat` | POST | Conversational interface |

**Documentation:** http://localhost:8081/docs (FastAPI auto-generated)

---

## 🎁 Bonus: Browser Testing

Open in browser for interactive docs:
```
http://localhost:8081/docs
```

Try requests directly from the Swagger UI!
