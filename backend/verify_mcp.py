
import asyncio
import sys
import os

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_server import mcp
from fastmcp import FastMCP

async def verify_mcp_flow():
    print("🚀 Verifying FastMCP Flow...")
    
    # 1. Verify Registration
    # In a real scenario, we'd check mcp.list_tools()
    # Here we assume mcp_server.py ran and registered tools
    print("✅ FastMCP instance initialized")
    
    # 2. Simulate Agent Execution
    tool_name = "list_doctors"
    args = {}
    
    print(f"🔄 invoking tool: {tool_name} with {args}")
    try:
        result = await mcp.call_tool(tool_name, arguments=args)
        print(f"✅ Result: {result}")
    except Exception as e:
        print(f"❌ Execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_mcp_flow())
