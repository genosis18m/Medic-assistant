
import asyncio
import os
import sys

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import chat

async def verify_email_override():
    print("🚀 Verifying Email Override & Name Capture...")
    
    # Context: User is logged in as 'mohit@gmail.com' but wants to book for 'friend@test.com'
    user_context = "User Email: mohit@gmail.com\nUser ID: 123"
    
    # Message explicitly asking for different email and specific name, AND providing reason
    message = "Book an appointment with Dr. Sarah Johnson for next Monday at 10:00 AM. Patient name is Noteen. Send confirmation to friend@test.com. Reason: Annual Checkup."
    
    print(f"\n📝 User Message: {message}")
    
    try:
        response, history, _ = await chat(message, role="patient", user_context=user_context)
        print(f"\n✅ Agent Response:\n{response}")
        
        # Check if the response reflects the overrides
        if "friend@test.com" in response or "Noteen" in response:
            print("\n✅ SUCCESS: Agent accepted the email/name override.")
        else:
            print("\n⚠️ WARNING: Response might not have confirmed the specific details. Check output.")
            
        # Check tool calls in history to see what was actually passed to the tool
        # The history contains the assistant's response which might include the tool call reasoning,
        # but the actual tool execution happened inside chat() and result was appended.
        # We can scan history for the 'tool' role or the function call details if preserved.
        
    except Exception as e:
        print(f"\n❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_email_override())
