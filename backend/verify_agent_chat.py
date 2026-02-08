
import asyncio
import os
import sys

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import chat

async def verify_chat():
    print("🚀 Verifying Agent Chat Flow...")
    
    # 1. Test simple chat
    print("\n1. Testing simple query...")
    try:
        response, _, _ = await chat("Hello, who are you?", role="patient")
        print(f"✅ Response: {response[:100]}...")
    except Exception as e:
        print(f"❌ Simple chat failed: {e}")
        
    # 2. Test tool usage (List Doctors)
    print("\n2. Testing tool usage (List Doctors)...")
    try:
        # We ask a question that triggers list_doctors
        response, _, _ = await chat("Which doctors are available?", role="patient")
        print(f"✅ Response: {response[:100]}...")
        if "Dr." in response:
            print("✅ Doctor names found in response")
        else:
            print("⚠️ logic might have skipped tool or LLM didn't use it, but no crash")
    except Exception as e:
        print(f"❌ Tool chat failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_chat())
