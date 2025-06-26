# AI Chatbot Configuration
# Copy this file to ai_config_local.py and update with your API keys

# OpenAI Configuration (Optional - for enhanced AI responses)
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY = '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'  # Set to your OpenAI API key for enhanced responses

# Chatbot Settings
CHATBOT_NAME = "Pigment"
CHATBOT_PERSONALITY = "friendly and helpful financial advisor"
MAX_CONVERSATION_HISTORY = 10
MAX_RESPONSE_LENGTH = 300

# Financial Context Settings
ENABLE_USER_CONTEXT = True  # Use user's financial data for personalized responses
ENABLE_CONVERSATION_HISTORY = True  # Remember previous conversations

# Fallback Settings
USE_INTELLIGENT_FALLBACK = True  # Use enhanced keyword matching when AI is unavailable
ENABLE_LOADING_INDICATOR = True  # Show "thinking" indicator

# Response Templates
DEFAULT_RESPONSES = {
    'greeting': "Hi! I'm Pigment, your AI financial assistant. How can I help you with your finances today?",
    'error': "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
    'no_understanding': "I'm not sure I understand. Could you rephrase that or ask me about budgeting, saving, investing, or using the Pigment app?",
    'loading': "🤔 Thinking..."
}

# Instructions for OpenAI API:
# 1. Sign up at https://platform.openai.com/
# 2. Get your API key from the API keys section
# 3. Set OPENAI_API_KEY = 'your-api-key-here'
# 4. The chatbot will automatically use OpenAI for enhanced responses
# 5. If no API key is provided, it will use intelligent keyword matching 