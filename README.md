# Early Intervention AI

##  Introduction

Early Intervention AI is an intelligent assistant designed to support early intervention specialists, therapists, and families working with young children (0-36 months) who have developmental needs. The application leverages artificial intelligence and retrieval-augmented generation (RAG) to provide evidence-based, age-appropriate intervention plans and conversational support.

##  Problem Statement

Early intervention professionals face several challenges:

1. **Time-Intensive Planning**: Creating individualized intervention plans requires extensive research and documentation time
2. **Knowledge Accessibility**: Practitioners need quick access to evidence-based strategies across multiple developmental domains
3. **Customization Complexity**: Each child has unique needs spanning multiple areas of concern
4. **Parent Engagement**: Families need practical, actionable advice that fits into daily routines
5. **Documentation Burden**: Detailed note-taking takes time away from direct service delivery

##  Our Solution

- **AI-Powered Plan Generation**: Creates comprehensive intervention plans tailored to child's age and concerns
- **Multiple Domain Support**: Handles complex cases across communication, social, motor, cognitive, and adaptive domains
- **Knowledge Base Integration**: Uses RAG to ground recommendations in evidence-based resources
- **Conversational Assistant**: Provides real-time guidance maintaining context about the child
- **Notes Tracking**: Captures observations for continuity of care
- **Family-Centered**: Generates practical advice for everyday activities

##  Tech Stack

**Frontend**: React 18, Material-UI v5, JavaScript ES6+, LocalStorage
**Backend**: FastAPI, Python 3.8+, LangChain, ChatGroq (llama-3.1-8b-instant)
**AI/ML**: ChromaDB, HuggingFace Embeddings, Sentence Transformers
**Data**: Pydantic validation, Vector embeddings, RAG

##  Installation

**Backend:**
```powershell
cd "C:\Users\STSC\Desktop\Therapy AI\v1_code"
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8081
```

**Frontend:**
```powershell
cd frontend
npm install
npm start
```

Access at: http://localhost:3000

## 📖 Use Case Example

**Scenario**: An early intervention specialist receives a referral for Emma, an 8-month-old infant showing delays in social interaction and motor skills.

**Step 1: Initial Assessment**
- Specialist opens the application and enters Emma's information:
  - Age: 8 months
  - Domains of concern: Social, Fine Motor, Gross Motor
  - Notes: "Unable to make sounds when playing; doesn't reach for toys; limited eye contact with parents"

**Step 2: Plan Generation**
- The AI generates a comprehensive intervention plan including:
  - **Social Domain**: Activities to encourage eye contact through peek-a-boo games, interactive songs, and responsive play
  - **Fine Motor**: Strategies for encouraging reaching and grasping using colorful toys, textured objects, and hand-over-hand support
  - **Gross Motor**: Exercises for tummy time, supported sitting, and transitional movements
  - Each activity includes age-appropriate adaptations and parent coaching tips

**Step 3: Conversational Support**
- During the session, the specialist uses the chat feature:
  - "What are some ways to encourage vocalization during play?"
  - AI provides evidence-based strategies using the knowledge base
  - Suggestions are contextualized for Emma's age and noted concerns

**Step 4: Progress Tracking**
- The specialist adds session notes: "Emma maintained eye contact for 3 seconds during song time; showed interest in rattle but didn't grasp"
- These notes are saved and can inform future plan generation
- Family receives practical homework activities aligned with daily routines (bath time, feeding, play)

**Outcome**: The specialist saves 30+ minutes on plan development while delivering a comprehensive, evidence-based intervention strategy tailored specifically for Emma's needs.

##  Future Enhancements

- Streaming responses
- Progress tracking
- PDF export
- Multi-language support
- Mobile app
- Telehealth integration
