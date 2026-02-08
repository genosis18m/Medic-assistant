"""
Agentic Brain: LLM Integration with Function Calling (OpenAI Edition)

This module sets up the OpenAI client with MCP tool definitions.
Supports both patient and doctor roles with context-aware prompts.
"""
import os
import json
import inspect
import asyncio
from datetime import date, datetime
from typing import Optional, Dict, Any, List, Union, get_origin, get_args
from dotenv import load_dotenv
from mcp_server import mcp
from schema_utils import get_openai_tools

# ============================================================================
# TOOL DEFINITIONS & FUNCTIONS
# ============================================================================

# We now use the MCP server instance for tool management
# mcp_server.py handles registration

# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

def get_system_prompt(role: str = "patient", context: str = "") -> str:
    """Get role-appropriate system prompt with current date context."""
    today = date.today()
    current_time = datetime.now().strftime("%H:%M")
    
    base_context = f"""Current Date: {today.strftime('%A, %B %d, %Y')}
    Current Time: {current_time}
    Today (ISO): {today.isoformat()}
    {context}
    """
    
    if role == "doctor":
        return f"""You are a smart medical assistant for doctors.

    {base_context}

    **OBJECTIVE**: Assist the doctor with their daily schedule, patient queries, and reports.
    
    **INSTRUCTIONS**: 
    - You have access to tools for checking stats, generating reports, and managing appointments. 
    - **Use your tools freely** to answer questions. Do not make up information.
    - If a user asks for a report (weekly/daily), use the appropriate report generation tool.
    - If sending to Telegram/Slack, ensure you have the necessary IDs or ask for them if missing.

    **Available Doctors**:
    - ID 1: Dr. Sarah Johnson (General)
    - ID 2: Dr. Michael Chen (Cardiology)
    - ID 3: Dr. Emily Williams (Dermatology)
    - ID 4: Dr. James Brown (Neurology)
    - ID 5: Dr. Mohit Adoni (General)
    """
    else:
        return f"""You are a helpful medical appointment assistant for patients.
        
    {base_context}

    **OBJECTIVE**: Help patients book, cancel, or view appointments.

    **INSTRUCTIONS**:
    - **Dynamic Booking**: To book an appointment, you must collect:
      1. **Date** & **Time**
      2. **Doctor**
      3. **Patient Name** & **Email**
      4. **Reason** for visit
    - **Email Handling**: You typically use the user's account email, BUT if the user explicitly asks to use a different email (e.g., "send to my other email" or "booking for a friend"), **YOU MUST USE THE REQUESTED EMAIL**. Do not refuse.
    - **Name Handling**: Record the patient name EXACTLY as provided by the user ("noteen" / noted exactly). Do not correct spelling or capitalization unless checking for clarity.
    - If details are missing, ask for them naturally.
    - **Availability**: Always check availability before confirming a specific slot.
    - **Tools**: Use `check_availability` to find slots and `book_appointment` to finalize.

    **Doctor IDs** (for internal use):
    - Mohit Adoni=5, Sarah Johnson=1, Michael Chen=2, Emily Williams=3, James Brown=4
    """

# ============================================================================
# CHAT LOGIC
# ============================================================================

async def chat(
    user_message: str,
    conversation_history: Optional[list] = None,
    role: str = "patient",
    user_context: str = ""
) -> tuple[str, list, list]:
    """
    Process message using OpenAI GPT-4o.
    """
    if conversation_history is None:
        conversation_history = []

    # Dynamic Tool Resolution Strategy
    # 1. Fetch all available tools from FastMCP registry
    # 2. Filter based on role permissions
    
    # Define allowed tool names for patients (whitelist approach for security)
    patient_allowed = {
        "check_availability", 
        "book_appointment", 
        "cancel_appointment", 
        "list_appointments",
        "list_doctors",
        "get_patient_history"
    }
    
    # Define doctor-only tools (or additional tools)
    doctor_allowed = {
        "get_appointment_stats", 
        "get_patient_stats", 
        "generate_summary_report",
        "send_slack_notification", 
        "send_report_to_telegram",
        "add_visit_notes", 
        "add_prescription", 
        "generate_patient_report"
    }

    # Filter tools from the registry
    registered_tools = getattr(mcp, "_tool_manager", None) and getattr(mcp._tool_manager, "_tools", {})
    if not registered_tools:
         # Try accessing direct .tools if future version
         registered_tools = getattr(mcp, "tools", {})

    tools_list = []
    
    if registered_tools:
        for name, tool_obj in registered_tools.items():
            if hasattr(tool_obj, 'func'):
                tool_func = tool_obj.func
            elif hasattr(tool_obj, 'fn'):
                tool_func = tool_obj.fn
            else:
                tool_func = tool_obj 

            if role == "patient" and name in patient_allowed:
                tools_list.append(tool_func)
            elif role == "doctor" and (name in patient_allowed or name in doctor_allowed):
                tools_list.append(tool_func)
    
    # Fallback if registry is empty
    if not tools_list:
        print("⚠️ Warning: Could not access FastMCP registry tools dynamically. Falling back to manual imports.")
        from tools.availability import check_availability
        from tools.booking import book_appointment, cancel_appointment, list_appointments
        from tools.patient_history import get_patient_history
        from tools.doctors import list_doctors
        
        tools_list = [
            list_doctors, check_availability, book_appointment, 
            cancel_appointment, list_appointments, get_patient_history
        ]
        
        if role == "doctor":
            from tools.doctor_reports import (
                get_appointment_stats, get_patient_stats, generate_summary_report,
                send_slack_notification, send_report_to_telegram
            )
            from tools.patient_history import (
                 add_visit_notes, add_prescription, generate_patient_report
            )
            tools_list.extend([
                get_appointment_stats, get_patient_stats, generate_summary_report,
                send_slack_notification, send_report_to_telegram,
                add_visit_notes, add_prescription, generate_patient_report
            ])

    # ------------------------------------------------------------------
    # OpenAI Execution
    # ------------------------------------------------------------------
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or not openai_key.startswith("sk-"):
        return "⚠️ Error: OPENAI_API_KEY is missing or invalid in backend/.env", conversation_history, []

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=openai_key)
        
        # Map tools to OpenAI format
        openai_tools = get_openai_tools(tools_list)

        # Convert System Prompt
        system_msg = {"role": "system", "content": get_system_prompt(role, user_context)}
        
        # Convert History
        # OpenAI expects: system, user, assistant, tool
        messages = [system_msg]
        if conversation_history:
            for msg in conversation_history:
                if msg['role'] == 'system': continue
                # OpenAI doesn't allow empty content for user messages usually, unless image
                content = msg.get('content') or ""
                if not content and not msg.get('tool_calls'): continue
                
                # We map 'tool' role to 'function' or 'tool' in OpenAI logic?
                # Our history format is simplified. Let's just pass user/assistant text for now
                if msg['role'] in ['user', 'assistant']:
                     messages.append({"role": msg['role'], "content": content})

        messages.append({"role": "user", "content": user_message})

        print(f"🤖 User asking OpenAI (gpt-4o)...")
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
        )

        response_msg = response.choices[0].message
        tool_calls = response_msg.tool_calls
        
        final_text = response_msg.content or ""
        
        if tool_calls:
            # Execute tools
            # We need to append the assistant's tool call message first
            # Convert to dict for safety with OpenAI client
            assistant_msg_dict = {
                "role": "assistant",
                "content": response_msg.content,
                "tool_calls": response_msg.tool_calls
            }
            messages.append(assistant_msg_dict)
            
            for tool_call in tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                print(f"🔧 OpenAI Tool Call: {fn_name} args={fn_args}")
                
                result = {"error": "Unknown tool"}
                
                try:
                    # Coerce ints - helper for better UX
                    for k in ["doctor_id", "limit", "appointment_id"]:
                        if k in fn_args:
                            try: fn_args[k] = int(fn_args[k])
                            except: pass
                    
                    # EXECUTE VIA MCP FRAMEWORK
                    mcp_result = await mcp.call_tool(fn_name, arguments=fn_args)
                    
                    # Extract text from result
                    result_text = ""
                    if isinstance(mcp_result, list):
                        for content in mcp_result:
                            if hasattr(content, 'text'):
                                result_text += content.text
                            else:
                                result_text += str(content)
                    else:
                        result_text = str(mcp_result)
                        
                    # Try to parse as JSON if it looks like it
                    try:
                        result = json.loads(result_text)
                    except:
                        result = result_text

                except Exception as e:
                    print(f"Tool Error: {e}")
                    result = {"error": str(e)}

                # Append tool result
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": fn_name,
                    "content": str(result)
                })
            
            # Get final response after tool outputs
            second_response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            final_text = second_response.choices[0].message.content

        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": final_text})
        return final_text, conversation_history, []

    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        return f"I'm sorry, I encountered an error: {e}", conversation_history, []
