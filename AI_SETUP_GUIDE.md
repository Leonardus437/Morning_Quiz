# AI Grading Setup Guide

## 🤖 Real AI-Powered Grading System

The system now supports **real AI models** for truly intelligent, human-like grading that understands concepts globally.

## How It Works

### 1. **AI Model Grading (Primary)**
When configured, the system uses real AI models (OpenAI GPT or AWS Bedrock) to:
- Understand the question context
- Analyze student's conceptual understanding
- Grade like an expert teacher
- Provide detailed, personalized feedback
- Award fair partial credit

### 2. **Semantic Fallback (Automatic)**
If AI is unavailable, automatically falls back to advanced semantic analysis.

## Setup Options

### Option A: OpenAI (Recommended - Easiest)

**Cost:** ~$0.002 per quiz submission (very cheap)

**Setup:**
1. Get API key from https://platform.openai.com/api-keys
2. Add to Render environment variables:
   ```
   OPENAI_API_KEY=sk-...your-key...
   ```
3. Restart backend service

**Benefits:**
- Best understanding of concepts
- Most human-like grading
- Supports all subjects globally
- Multilingual (English, French, Kinyarwanda)

### Option B: AWS Bedrock (Enterprise)

**Cost:** ~$0.001 per quiz submission

**Setup:**
1. Enable AWS Bedrock in your AWS account
2. Add to Render environment variables:
   ```
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_REGION=us-east-1
   ```
3. Restart backend service

**Benefits:**
- Lower cost at scale
- Data stays in your AWS account
- Enterprise-grade security

### Option C: No Setup (Free Fallback)

**Cost:** Free

**Setup:** Nothing - works automatically

**Benefits:**
- No API keys needed
- No external dependencies
- Still provides intelligent grading
- Good for testing

## Grading Quality Comparison

| Feature | OpenAI/Bedrock | Semantic Fallback |
|---------|----------------|-------------------|
| Conceptual Understanding | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Context Awareness | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Multilingual | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Partial Credit | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Speed | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Cost | ~$0.002/quiz | Free |

## Example Grading

### Question: "Explain how photosynthesis works"

**Model Answer:** "Plants use sunlight, water, and carbon dioxide to produce glucose and oxygen through chlorophyll in their leaves"

**Student Answers with AI Grading:**

1. **"Plants make food using sun, water and CO2, releasing oxygen"**
   - AI Score: 9/10
   - Feedback: "Excellent - demonstrates complete understanding of the process and products"

2. **"Chlorophyll in leaves captures light energy to convert water and carbon dioxide into sugar"**
   - AI Score: 9.5/10
   - Feedback: "Outstanding - includes key mechanism and accurate chemistry"

3. **"Plants use sunlight to make food"**
   - AI Score: 6/10
   - Feedback: "Basic understanding shown but missing key details about reactants and products"

4. **"Photosynthesis is when plants breathe"**
   - AI Score: 2/10
   - Feedback: "Incorrect - confuses photosynthesis with respiration"

## How to Enable

### On Render (Production):

1. Go to https://dashboard.render.com
2. Select your backend service
3. Go to "Environment" tab
4. Add environment variable:
   - Key: `OPENAI_API_KEY`
   - Value: `sk-...your-key...`
5. Click "Save Changes"
6. Service will auto-restart

### Testing Locally:

Create `.env` file in `backend/` folder:
```bash
OPENAI_API_KEY=sk-...your-key...
```

Or export in terminal:
```bash
export OPENAI_API_KEY=sk-...your-key...
cd backend
python -m uvicorn main:app --reload
```

## Cost Estimation

### For 100 Students Taking 10 Quizzes Each:
- Total submissions: 1,000
- Questions per quiz: ~10
- Total gradings: 10,000
- **OpenAI Cost: ~$20/month**
- **Bedrock Cost: ~$10/month**
- **Fallback Cost: $0**

### For 500 Students:
- **OpenAI Cost: ~$100/month**
- **Bedrock Cost: ~$50/month**

## Verification

Check if AI grading is active:

1. Submit a test quiz
2. Check backend logs for:
   - ✅ "Using OpenAI for grading" - AI active
   - ⚠️ "OpenAI grading failed" - Fallback used
   - ℹ️ No message - Fallback used (no API key)

## Benefits of AI Grading

### For Teachers:
- **Zero manual grading** - AI handles everything
- **Consistent standards** - Same quality for all students
- **Detailed feedback** - Students learn from mistakes
- **Time savings** - Focus on teaching, not grading
- **Fair assessment** - No unconscious bias

### For Students:
- **Instant results** - No waiting for grades
- **Fair evaluation** - Credit for understanding, not memorization
- **Helpful feedback** - Learn what to improve
- **Reduced anxiety** - Objective, consistent grading
- **Multiple attempts** - Practice without judgment

## Troubleshooting

### "AI grading not working"
1. Check API key is set in Render environment
2. Verify key is valid at OpenAI dashboard
3. Check backend logs for error messages
4. System will use fallback automatically

### "Grading seems too strict/lenient"
- AI is calibrated to be fair and generous
- Adjust by modifying prompt in `ai_grader.py`
- Contact support for custom calibration

### "Want to use different AI model"
- Edit `ai_grader.py` line with model name
- Options: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`
- GPT-4 is more accurate but 10x more expensive

## Security

- API keys stored securely in Render environment
- Keys never exposed to frontend
- All grading happens server-side
- Student answers not stored by OpenAI (per API terms)

## Next Steps

1. **Get OpenAI API key** (5 minutes)
2. **Add to Render** (2 minutes)
3. **Test with quiz** (5 minutes)
4. **Enjoy AI grading!** ✨

---

**The system works perfectly without AI setup, but adding AI makes it truly exceptional!**
