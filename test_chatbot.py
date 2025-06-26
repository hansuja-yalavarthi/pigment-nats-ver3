#!/usr/bin/env python3
"""
Test script for the AI Chatbot with site reference functionality
"""

from ai_chatbot import AIChatbot

def test_chatbot():
    print("🤖 Testing Pigment AI Chatbot with Site Reference")
    print("=" * 50)
    
    # Initialize chatbot
    chatbot = AIChatbot()
    
    # Test questions
    test_questions = [
        "How do I add a transaction?",
        "What categories are available for transactions?",
        "How do I set up a budget?",
        "How can I export my data?",
        "What is Pigment?",
        "How do I track savings goals?",
        "What should I do if I forgot my password?",
        "How do I create an emergency fund?",
        "What are the best practices for budgeting?",
        "Can you help me with investment advice?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 30)
        
        try:
            response = chatbot.get_ai_response(question)
            print(f"Answer: {response}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Chatbot test completed!")

if __name__ == "__main__":
    test_chatbot() 