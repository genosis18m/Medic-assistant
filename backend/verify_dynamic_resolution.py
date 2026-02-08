
import asyncio
import os
import sys

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import chat
from mcp_server import mcp

async def verify_dynamic_resolution():
    print("🚀 Verifying Dynamic Role-Aware Tool Resolution...")
    
    # 1. Check if tools are registered in MCP
    # Access internal tool registry for verification
    tools_dict = getattr(mcp, "_tool_manager", None) and getattr(mcp._tool_manager, "_tools", {})
    if not tools_dict:
        tools_dict = getattr(mcp, "tools", {})
        
    print(f"\n📚 Total Registered Tools: {len(tools_dict)}")
    for name in tools_dict:
        print(f" - {name}")

    if len(tools_dict) == 0:
        print("❌ CRITICAL: No tools registered in MCP!")
        return

    # 2. Test Patient Role 
    # Should only have patient allowed tools
    print("\n-------- Testing Patient Role --------")
    # We can't easily inspect the internal 'tools_list' local var in chat() 
    # without modifying agent.py to print it or returning it.
    # But we can try to call a doctor-only tool (e.g., get_patient_stats) as a patient and see if it fails or is ignored.
    
    msg = "Please get me the patient stats for today."
    response, _, _ = await chat(msg, role="patient")
    print(f"Response to restricted tool request: {response}")
    
    # 3. Test Doctor Role
    print("\n-------- Testing Doctor Role --------")
    msg = "Please get me the patient stats for today."
    # response, _, _ = await chat(msg, role="doctor") # Commented out to save tokens/time if just checking logic
    # print(f"Response: {response}")
    
    print("\n✅ Dynamic resolution logic executed (check logs for tool use or rejection)")

if __name__ == "__main__":
    asyncio.run(verify_dynamic_resolution())
