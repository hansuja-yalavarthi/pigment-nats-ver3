import os
import json
import requests
from datetime import datetime
import sqlite3
from typing import Dict, List, Optional

# Import site reference
try:
    from site_reference import SITE_REFERENCE, search_site_reference, get_site_info
except ImportError:
    # Fallback if site reference is not available
    SITE_REFERENCE = {}
    def search_site_reference(query):
        return []
    def get_site_info(category=None, subcategory=None):
        return {}

# Load configuration
try:
    from ai_config import *
except ImportError:
    # Default configuration if file doesn't exist
    OPENAI_API_KEY = None
    CHATBOT_NAME = "Pigment"
    CHATBOT_PERSONALITY = "friendly and helpful financial advisor"
    MAX_CONVERSATION_HISTORY = 10
    MAX_RESPONSE_LENGTH = 300
    ENABLE_USER_CONTEXT = True
    ENABLE_CONVERSATION_HISTORY = True
    USE_INTELLIGENT_FALLBACK = True
    ENABLE_LOADING_INDICATOR = True
    DEFAULT_RESPONSES = {
        'greeting': "Hi! I'm Pigment, your AI financial assistant. How can I help you with your finances today?",
        'error': "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
        'no_understanding': "I'm not sure I understand. Could you rephrase that or ask me about budgeting, saving, investing, or using the Pigment app?",
        'loading': "🤔 Thinking..."
    }

class AIChatbot:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.conversation_history = []
        self.financial_context = self._get_financial_context()
        
    def _get_financial_context(self) -> str:
        """Get the financial context for the AI"""
        return f"""
        You are {CHATBOT_NAME}, an AI financial assistant for a personal finance app. Your personality is {CHATBOT_PERSONALITY}. Your role is to help users with:
        
        1. **Budgeting Advice**: Help users create and manage budgets, understand spending patterns, and set financial goals
        2. **Financial Education**: Explain financial concepts, provide tips for saving money, and offer investment guidance
        3. **App Features**: Explain how to use the Pigment app features like transaction tracking, budget setting, and savings goals
        4. **Personal Finance**: Answer questions about debt management, emergency funds, retirement planning, and financial planning
        
        Key Features of the Pigment App:
        - Transaction tracking and categorization
        - Budget setting and monitoring
        - Savings goals with target amounts and due dates
        - Financial reports and analytics
        - Export functionality (CSV/PDF)
        
        Always be helpful, friendly, and provide actionable advice. Keep responses under {MAX_RESPONSE_LENGTH} characters. If you don't know something specific about the app's features, suggest they check the app's help section or contact support.
        """
    
    def get_ai_response(self, user_message: str, user_data: Optional[Dict] = None) -> str:
        """Get AI response using OpenAI API or fallback to intelligent keyword matching"""
        
        # First, check if this is a site-specific question
        site_response = self._check_site_reference(user_message)
        if site_response:
            return site_response
        
        # Try OpenAI API first if available
        if self.api_key:
            try:
                return self._get_openai_response(user_message, user_data)
            except Exception as e:
                print(f"OpenAI API error: {e}")
                if USE_INTELLIGENT_FALLBACK:
                    return self._get_intelligent_response(user_message, user_data)
                else:
                    return DEFAULT_RESPONSES['error']
        else:
            # Use intelligent keyword matching if no API key
            return self._get_intelligent_response(user_message, user_data)
    
    def _check_site_reference(self, user_message: str) -> Optional[str]:
        """Check if the user's question can be answered using the site reference"""
        user_message_lower = user_message.lower()
        
        # Check for specific common questions first
        common_questions = SITE_REFERENCE.get('common_questions', {})
        for question_key, question_data in common_questions.items():
            if isinstance(question_data, dict) and 'question' in question_data:
                question_text = question_data['question'].lower()
                # Check if the user's message contains key words from the question
                question_words = question_text.split()
                if any(word in user_message_lower for word in question_words if len(word) > 3):
                    return question_data.get('answer', '')
        
        # Check for specific keywords and provide targeted responses
        if any(word in user_message_lower for word in ['category', 'categories']):
            categories_info = SITE_REFERENCE.get('core_features', {}).get('transaction_tracking', {}).get('categories', [])
            if categories_info:
                return f"Available categories include: {', '.join(categories_info)}. You can also add custom descriptions to transactions."
        
        if any(word in user_message_lower for word in ['export', 'download', 'csv', 'pdf']):
            export_info = SITE_REFERENCE.get('core_features', {}).get('data_export', {})
            if export_info:
                return f"{export_info.get('description', '')} {export_info.get('how_to', '')}"
        
        if any(word in user_message_lower for word in ['budget', 'budgeting']):
            budget_info = SITE_REFERENCE.get('core_features', {}).get('budget_management', {})
            if budget_info:
                return f"{budget_info.get('description', '')} {budget_info.get('how_to', '')}"
        
        if any(word in user_message_lower for word in ['savings', 'goal', 'goals']):
            savings_info = SITE_REFERENCE.get('core_features', {}).get('savings_goals', {})
            if savings_info:
                return f"{savings_info.get('description', '')} {savings_info.get('how_to', '')}"
        
        if any(word in user_message_lower for word in ['password', 'forgot', 'reset']):
            return "If you forgot your password, use the 'Forgot Password' link on the login page. You'll receive a password reset link via email."
        
        if any(word in user_message_lower for word in ['pigment', 'app', 'what is']):
            app_info = SITE_REFERENCE.get('app_description', '')
            if app_info:
                return app_info
        
        if any(word in user_message_lower for word in ['emergency', 'fund']):
            return "An emergency fund is your financial safety net! Aim to save 3-6 months of living expenses. Start small - even $500 can help with unexpected car repairs or medical bills. Pigment can help you track your emergency fund progress."
        
        if any(word in user_message_lower for word in ['best practice', 'practice', 'tip', 'advice']):
            practices = SITE_REFERENCE.get('best_practices', {})
            if practices:
                response_parts = []
                for category, tips in practices.items():
                    if isinstance(tips, list):
                        response_parts.append(f"{category.title()}: {', '.join(tips)}")
                if response_parts:
                    return " ".join(response_parts)
        
        if any(word in user_message_lower for word in ['investment', 'invest', 'stock', 'retirement']):
            return "Investing is important for long-term wealth building! Start with retirement accounts like 401(k)s or IRAs. Consider low-cost index funds for beginners. Remember: time in the market beats timing the market. Always do your research!"
        
        # If no specific match found, search the site reference for relevant information
        search_results = search_site_reference(user_message)
        
        if search_results:
            # Build a response based on the search results
            response_parts = []
            for result in search_results[:2]:  # Limit to top 2 results
                if result['key'] == 'answer':
                    response_parts.append(result['value'])
                elif result['key'] == 'description':
                    response_parts.append(f"{result['subcategory'].replace('_', ' ').title()}: {result['value']}")
                elif result['key'] == 'how_to':
                    response_parts.append(f"How to use {result['subcategory'].replace('_', ' ')}: {result['value']}")
            
            if response_parts:
                return " ".join(response_parts)
        
        return None
    
    def _get_openai_response(self, user_message: str, user_data: Optional[Dict] = None) -> str:
        """Get response from OpenAI API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Build context with user data and site reference if available
        context = self.financial_context
        
        # Add site reference information to context
        if SITE_REFERENCE:
            context += f"\n\nSite Information: {json.dumps(SITE_REFERENCE, indent=2)}"
        
        if user_data and ENABLE_USER_CONTEXT:
            context += f"\n\nUser Context: {json.dumps(user_data, indent=2)}"
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': context},
                {'role': 'user', 'content': user_message}
            ],
            'max_tokens': MAX_RESPONSE_LENGTH,
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            raise Exception(f"OpenAI API error: {response.status_code}")
    
    def _get_intelligent_response(self, user_message: str, user_data: Optional[Dict] = None) -> str:
        """Intelligent keyword matching with context awareness"""
        
        user_message_lower = user_message.lower()
        
        # Enhanced keyword responses with more context
        responses = {
            # Budgeting
            'budget': {
                'keywords': ['budget', 'budgeting', 'spending limit', 'financial plan'],
                'response': "Creating a budget is essential for financial success! In Pigment, you can set budget limits for different categories like food, entertainment, and utilities. Track your spending against these limits to stay on track. Would you like help setting up a specific budget category?"
            },
            
            # Savings
            'savings': {
                'keywords': ['save', 'saving', 'savings goal', 'emergency fund', 'money saved'],
                'response': "Great question about savings! Pigment helps you set and track savings goals. You can create goals for anything - emergency funds, vacations, or big purchases. Set a target amount and due date, then track your progress. What are you saving for?"
            },
            
            # Spending tracking
            'tracking': {
                'keywords': ['track', 'tracking', 'expenses', 'spending', 'transactions'],
                'response': "Pigment makes tracking your spending easy! Every transaction you add is automatically categorized and compared to your budget. You can see spending patterns, identify areas to cut back, and stay accountable to your financial goals."
            },
            
            # Financial goals
            'goals': {
                'keywords': ['goal', 'goals', 'financial goal', 'target', 'objective'],
                'response': "Setting financial goals is key to success! In Pigment, you can create multiple savings goals with target amounts and deadlines. Whether it's an emergency fund, vacation, or debt payoff, having clear goals keeps you motivated and focused."
            },
            
            # Debt management
            'debt': {
                'keywords': ['debt', 'loan', 'credit card', 'pay off', 'borrow'],
                'response': "Managing debt is crucial for financial health! Focus on paying off high-interest debt first, like credit cards. Consider the debt snowball or avalanche method. Pigment can help you track your debt payoff progress and stay motivated."
            },
            
            # Investment
            'investment': {
                'keywords': ['invest', 'investment', 'stock', 'retirement', '401k', 'ira'],
                'response': "Investing is important for long-term wealth building! Start with retirement accounts like 401(k)s or IRAs. Consider low-cost index funds for beginners. Remember: time in the market beats timing the market. Always do your research!"
            },
            
            # Emergency fund
            'emergency': {
                'keywords': ['emergency', 'emergency fund', 'rainy day', 'unexpected'],
                'response': "An emergency fund is your financial safety net! Aim to save 3-6 months of living expenses. Start small - even $500 can help with unexpected car repairs or medical bills. Pigment can help you track your emergency fund progress."
            },
            
            # App features
            'features': {
                'keywords': ['feature', 'function', 'how to', 'help', 'guide'],
                'response': "Pigment offers many helpful features! Track transactions, set budgets, create savings goals, export reports, and get insights into your spending. What specific feature would you like to learn more about?"
            },
            
            # Reports and analytics
            'reports': {
                'keywords': ['report', 'analytics', 'export', 'pdf', 'csv', 'data'],
                'response': "Pigment provides detailed reports and analytics! Export your transaction data as CSV or PDF files. View spending patterns, budget progress, and savings goal status. These insights help you make better financial decisions."
            },
            
            # General financial advice
            'general': {
                'keywords': ['advice', 'tip', 'help', 'suggestion', 'recommend'],
                'response': "Here are some general financial tips: 1) Pay yourself first - save before spending, 2) Track every expense, 3) Build an emergency fund, 4) Pay off high-interest debt, 5) Start investing early. What specific area would you like advice on?"
            }
        }
        
        # Check for matches and return the best response
        for category, data in responses.items():
            for keyword in data['keywords']:
                if keyword in user_message_lower:
                    return data['response']
        
        # Default response for unrecognized queries
        return DEFAULT_RESPONSES['no_understanding']
    
    def get_user_financial_context(self, username: str) -> Dict:
        """Get user's financial context from their database"""
        try:
            # This would connect to the user's specific database
            # For now, return a basic structure
            return {
                'username': username,
                'has_transactions': True,
                'has_budgets': True,
                'has_savings_goals': True
            }
        except Exception as e:
            print(f"Error getting user context: {e}")
            return {}
    
    def add_to_history(self, user_message: str, bot_response: str):
        """Add conversation to history"""
        if ENABLE_CONVERSATION_HISTORY:
            self.conversation_history.append({
                'user_message': user_message,
                'bot_response': bot_response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only the last N conversations
            if len(self.conversation_history) > MAX_CONVERSATION_HISTORY:
                self.conversation_history = self.conversation_history[-MAX_CONVERSATION_HISTORY:]
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history.copy() 