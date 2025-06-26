#!/usr/bin/env python3
"""
Test OpenAI integration for the AI Chatbot
"""

from ai_chatbot import AIChatbot

def test_openai():
    print("🤖 Testing OpenAI Integration")
    print("=" * 40)
    
    # Initialize chatbot
    chatbot = AIChatbot()
    
    # Test questions that should use OpenAI
    test_questions = [
        "Hello, how are you?",
        "What is the best way to start saving money?",
        "Can you give me some investment advice?",
        "How should I budget my monthly income?",
        "What are some good financial habits?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 30)
        
        try:
            response = chatbot.get_ai_response(question)
            print(f"Response: {response}")
            print(f"Response length: {len(response)} characters")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 40)
    print("✅ OpenAI test completed!")

if __name__ == "__main__":
    test_openai() 