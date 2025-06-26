# AI Chatbot Setup for Pigment Flask App

This document explains how to set up and use the AI-powered chatbot for the Pigment Flask application.

## Features

✅ **AI-Powered Responses**: Uses OpenAI GPT-3.5 for intelligent financial advice
✅ **Intelligent Fallback**: Enhanced keyword matching when AI is unavailable
✅ **Financial Context**: Understands personal finance and Pigment app features
✅ **Conversation History**: Remembers previous conversations
✅ **User Context**: Can use user's financial data for personalized responses
✅ **Loading Indicators**: Shows "thinking" indicator during AI processing
✅ **Error Handling**: Graceful fallback when AI services are unavailable

## Setup Instructions

### 1. Install Dependencies

The AI chatbot dependencies are already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Configure AI Settings (Optional)

For enhanced AI responses, you can set up OpenAI API:

1. **Get OpenAI API Key**:
   - Sign up at https://platform.openai.com/
   - Go to API Keys section
   - Create a new API key

2. **Configure the API Key**:
   ```bash
   cp ai_config.py ai_config_local.py
   ```
   
   Edit `ai_config_local.py`:
   ```python
   OPENAI_API_KEY = 'your-openai-api-key-here'
   ```

### 3. Test the Chatbot

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Login to your account**

3. **Click the chatbot button** (💬) in the bottom-right corner

4. **Try these example questions**:
   - "How do I create a budget?"
   - "What should I save for an emergency fund?"
   - "How can I track my spending?"
   - "What are good investment strategies?"
   - "How do I use the Pigment app features?"

## How It Works

### AI Response Flow

1. **User sends message** → Chatbot receives input
2. **Check for OpenAI API** → If available, use GPT-3.5
3. **Get AI response** → Generate contextual financial advice
4. **Fallback system** → If AI fails, use intelligent keyword matching
5. **Return response** → Send helpful, actionable advice

### Intelligent Fallback System

When OpenAI API is unavailable or not configured, the chatbot uses enhanced keyword matching with:

- **Financial categories**: Budgeting, saving, investing, debt management
- **App features**: Transaction tracking, budget setting, reports
- **Personal finance**: Emergency funds, retirement planning, financial goals
- **Context-aware responses**: Tailored to Pigment app capabilities

### Conversation Features

- **History tracking**: Remembers last 10 conversations
- **User context**: Can access user's financial data (future enhancement)
- **Loading indicators**: Shows "🤔 Thinking..." during processing
- **Error handling**: Graceful fallback with helpful messages

## Configuration Options

Edit `ai_config.py` to customize the chatbot:

```python
# Chatbot Settings
CHATBOT_NAME = "Pigment"
CHATBOT_PERSONALITY = "friendly and helpful financial advisor"
MAX_CONVERSATION_HISTORY = 10
MAX_RESPONSE_LENGTH = 300

# Features
ENABLE_USER_CONTEXT = True
ENABLE_CONVERSATION_HISTORY = True
USE_INTELLIGENT_FALLBACK = True
ENABLE_LOADING_INDICATOR = True
```

## API Endpoints

### POST /chatbot
Send a message to the AI chatbot:
```json
{
  "message": "How do I create a budget?"
}
```

Response:
```json
{
  "response": "Creating a budget is essential for financial success! In Pigment...",
  "timestamp": "2025-01-20T13:30:00"
}
```

### GET /chatbot/history
Get conversation history:
```json
{
  "history": [
    {
      "timestamp": "2025-01-20T13:30:00",
      "user": "How do I create a budget?",
      "bot": "Creating a budget is essential..."
    }
  ]
}
```

## Financial Topics Covered

The AI chatbot is trained on:

### Budgeting
- Creating and managing budgets
- Setting spending limits
- Tracking expenses
- Budget categories

### Saving
- Emergency funds
- Savings goals
- Saving strategies
- Financial planning

### Investing
- Retirement planning
- Investment basics
- 401(k) and IRA accounts
- Risk management

### Debt Management
- Credit card debt
- Loan repayment strategies
- Debt snowball/avalanche methods
- Credit score improvement

### Pigment App Features
- Transaction tracking
- Budget setting
- Savings goals
- Reports and analytics
- Export functionality

## Troubleshooting

### Chatbot Not Responding
1. Check browser console for JavaScript errors
2. Verify the Flask app is running
3. Check if the `/chatbot` endpoint is accessible

### AI Responses Not Working
1. Verify OpenAI API key is correct
2. Check internet connection
3. The fallback system should work even without AI

### Slow Responses
1. AI responses may take 2-5 seconds
2. Check your internet connection
3. Consider using the fallback system for faster responses

## Security Notes

- **API Keys**: Never commit API keys to version control
- **User Data**: Chatbot can access user context but doesn't store sensitive data
- **Conversation History**: Stored temporarily in memory, not persisted
- **Rate Limiting**: Consider implementing rate limiting for production

## Production Deployment

For production deployment:

1. **Use environment variables** for API keys
2. **Implement rate limiting** to prevent abuse
3. **Add monitoring** for chatbot usage
4. **Consider caching** for common responses
5. **Set up logging** for debugging

## File Structure

```
pigment-nats-ver1/
├── ai_chatbot.py              # AI chatbot service
├── ai_config.py               # Chatbot configuration
├── app.py                     # Main Flask app (updated)
├── templates/
│   └── index.html             # Updated with AI chatbot
└── README_AI_CHATBOT.md       # This file
```

The AI chatbot is now fully integrated and ready to provide intelligent financial assistance to your users! 