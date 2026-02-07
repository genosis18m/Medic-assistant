"""
Agentic Brain: LLM Integration with Function Calling (Gemini Edition)

This module sets up the Google Gemini client with MCP tool definitions.
Supports both patient and doctor roles with context-aware prompts.
"""
import os
import json
import inspect
import asyncio
from datetime import date, datetime
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from google.api_core.exceptions import InvalidArgument
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Import tools
from tools.availability import check_availability
from tools.booking import book_appointment, cancel_appointment, list_appointments
from tools.doctor_reports import (
    get_appointment_stats,
    get_patient_stats,
    generate_summary_report,
    send_slack_notification,
    send_report_to_telegram
)
from tools.patient_history import (
    get_patient_history,
    add_visit_notes,
    add_prescription,
    generate_patient_report
)
from tools.doctors import list_doctors

load_dotenv()

# Configure Gemini
# In production, use os.getenv("GEMINI_API_KEY")
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDekQ53PPEkiuO8ZnQ0MREBtnuA2EjvSb4")
genai.configure(api_key=API_KEY)

# ============================================================================
# TOOL DEFINITIONS & FUNCTIONS
# ============================================================================

# Tools enabled for the model
patient_tools_funcs = [
    list_doctors,
    check_availability,
    book_appointment,
    cancel_appointment,
    list_appointments,
    get_patient_history
]

doctor_tools_funcs = patient_tools_funcs + [
    get_appointment_stats,
    get_patient_stats,
    generate_summary_report,
    send_slack_notification,
    send_report_to_telegram
]

# Map for execution
TOOL_FUNCTIONS = {f.__name__: f for f in doctor_tools_funcs}

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

    **CAPABILITIES**:
    1. **Stats**: "How many appointments today?" (Use `get_appointment_stats`)
    2. **Reports**: "Weekly report" (Use `generate_summary_report`)
    3. **Patient Queries**: "Patients with fever" (Use `get_patient_stats`)
    4. **Manage**: Book/Cancel appointments.

    - **TELEGRAM/PDF**: If the user asks for a Telegram report:
      1. **Check**: Did the user provide a Chat ID? (e.g., "123456789")
      2. **If NO**: Reply EXACTLY: "I need your Telegram Chat ID to send the report. Please start the bot @Doctor_AssistBot, find your numeric ID (you can use @userinfobot), and paste it here."
      3. **If YES**: Call `send_report_to_telegram(doctor_id=..., chat_id='...')`.
    - **ID**: Always use the `doctor_id` from context.

    Available doctors:
    - ID 1: Dr. Sarah Johnson (General)
    - ID 2: Dr. Michael Chen (Cardiology)
    - ID 3: Dr. Emily Williams (Dermatology)
    - ID 4: Dr. James Brown (Neurology)
    - ID 5: Dr. Mohit Adoni (General)
    """
    else:
        return f"""You are a helpful medical appointment assistant.
        
    {base_context}

    **BOOKING STEPS (STRICTLY ONE BY ONE)**:
    1. **Date/Time**: "When would you like to come in?" (Wait for answer).
    2. **Doctor**: "Which doctor would you like to see?" (If unknown, offer to list them).
    3. **Availability**: Call `check_availability`. Present slots clearly.
    4. **Name**: "Could you please provide your full name?"
    5. **Email**: "What is your email address?" (If they say 'same as login', confirm it).
    6. **Reason**: "What is the reason for your visit?"
    7. **Confirm**: "Just to check: [Recap details]. Shall I confirm this booking?"
    8. **Book**: Call `book_appointment`.
    
    **TONE**: Professional, polite, and efficient. Do not bundle questions (e.g., do NOT ask for Name, Email, and Reason in one message). Ask separately.

    Doctor IDs: Mohit Adoni=5, Sarah Johnson=1, Michael Chen=2, Emily Williams=3, James Brown=4
    """

# ============================================================================
# CHAT LOGIC
# ============================================================================

# ============================================================================
# CHAT LOGIC
# ============================================================================

# Models to try in order of preference/stability/quota probability
FALLBACK_MODELS = [
    "gemini-1.5-flash",          # Standard efficient model
    "gemini-1.5-flash-001",      # Versioned stable
    "gemini-1.5-flash-latest",   # Latest alias
    "gemini-1.5-pro",           # Higher tier
    "gemini-1.5-pro-001",
    "gemini-pro",               # Legacy stable
    "gemini-flash-latest",      # Maps to 2.5-flash (Daily Limit)
    "gemini-2.0-flash-lite",    # Experimental
    "gemini-2.0-flash"          # Experimental
]

async def chat(
    user_message: str,
    conversation_history: Optional[list] = None,
    role: str = "patient",
    user_context: str = ""
) -> tuple[str, list, list]:
    """
    Process message using OpenAI GPT-4o (if trusted) or Gemini with automatic fallback.
    """
    if conversation_history is None:
        conversation_history = []

    # Select tools based on role
    tools_list = doctor_tools_funcs if role == "doctor" else patient_tools_funcs
    
    # ------------------------------------------------------------------
    # 1. Try OPENAI if Key Exists
    # ------------------------------------------------------------------
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.startswith("sk-"):
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=openai_key)
            
            # Map tools to OpenAI format
            openai_tools = []
            for func in tools_list:
                # Basic conversion of python function to OpenAI tool schema
                # For full robustness, we'd use pydantic or langchain, but here we do basic inspection
                # Assuming tools are well documented functions
                sig = inspect.signature(func)
                doc = func.__doc__ or ""
                
                params = {}
                required = []
                for name, param in sig.parameters.items():
                    p_type = "string"
                    if param.annotation == int: p_type = "integer"
                    if param.annotation == bool: p_type = "boolean"
                    
                    params[name] = {
                        "type": p_type,
                        "description": f"Parameter {name}"
                    }
                    if param.default == inspect.Parameter.empty:
                        required.append(name)
                        
                tool_def = {
                    "type": "function",
                    "function": {
                        "name": func.__name__,
                        "description": doc.strip(),
                        "parameters": {
                            "type": "object",
                            "properties": params,
                            "required": required
                        }
                    }
                }
                openai_tools.append(tool_def)

            # Convert System Prompt
            system_msg = {"role": "system", "content": get_system_prompt(role, user_context)}
            
            # Convert History
            # OpenAI expects: system, user, assistant, tool
            messages = [system_msg]
            for msg in conversation_history:
                if msg['role'] == 'system': continue
                # OpenAI doesn't allow empty content for user messages usually, unless image
                content = msg.get('content') or ""
                if not content and not msg.get('tool_calls'): continue
                
                # We map 'tool' role to 'function' or 'tool' in OpenAI logic?
                # Our history format is simplified. Let's just pass user/assistant text for now
                # to avoid complexity with tool_call_id matching in history reconstruction
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
                messages.append(response_msg)
                
                for tool_call in tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)
                    print(f"🔧 OpenAI Tool Call: {fn_name} args={fn_args}")
                    
                    result = {"error": "Unknown tool"}
                    if fn_name in TOOL_FUNCTIONS:
                         try:
                            # Coerce ints
                            for k in ["doctor_id", "limit", "appointment_id"]:
                                if k in fn_args:
                                    try: fn_args[k] = int(fn_args[k])
                                    except: pass

                            func = TOOL_FUNCTIONS[fn_name]
                            if inspect.iscoroutinefunction(func):
                                result = await func(**fn_args)
                            else:
                                result = func(**fn_args)
                         except Exception as e:
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
            print(f"⚠️ OpenAI Error: {e}. Falling back to Gemini...")
            # Fall through to Gemini logic
    
    # ------------------------------------------------------------------
    # 2. Fallback to GEMINI
    # ------------------------------------------------------------------
    
    # Convert history for Gemini
    gemini_history = []
    for msg in conversation_history:
        if msg['role'] == 'system': continue
        g_role = 'user' if msg['role'] == 'user' else 'model'
        content = msg.get('content', '')
        if not content and not msg.get('tool_calls'): continue
        gemini_history.append({'role': g_role, 'parts': [content]})

    last_error = None
    
    # Try models in sequence
    for model_name in FALLBACK_MODELS:
        try:
            print(f"🔄 Attempting with model: {model_name}")
            model = genai.GenerativeModel(
                model_name=model_name,
                tools=tools_list,
                system_instruction=get_system_prompt(role, user_context)
            )

            # Start chat
            chat_session = model.start_chat(history=gemini_history)
            
            # Send message
            response = chat_session.send_message(user_message)
            
            # If we get here, the model worked! Process the response.
            
            final_text = ""
            user_actions = []
            
            # Handle Function Calls
            while True:
                # Check for function call in the response
                part = response.parts[0] if response.parts else None
                
                if part and part.function_call:
                    fn = part.function_call
                    fn_name = fn.name
                    fn_args = dict(fn.args)
                    print(f"🔧 Tool Call ({model_name}): {fn_name}")
                    
                    result = {"error": "Unknown tool"}
                    if fn_name in TOOL_FUNCTIONS:
                        # Coerce ints
                        for k in ["doctor_id", "limit", "appointment_id"]:
                            if k in fn_args:
                                try: fn_args[k] = int(fn_args[k])
                                except: pass
                        
                        try:
                            func = TOOL_FUNCTIONS[fn_name]
                            if inspect.iscoroutinefunction(func):
                                result = await func(**fn_args)
                            else:
                                result = func(**fn_args)
                        except Exception as e:
                            result = {"error": str(e)}
                    
                    # Send result back
                    try:
                        response = chat_session.send_message(
                            genai.protos.Content(
                                parts=[genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=fn_name,
                                        response={"result": result}
                                    )
                                )]
                            )
                        )
                    except Exception as e:
                        print(f"Tool reply error ({model_name}): {e}")
                        final_text = str(result)
                        break
                else:
                    final_text = response.text
                    break

            # Success! Update history and return
            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": final_text})
            return final_text, conversation_history, user_actions

        except Exception as e:
            error_str = str(e)
            print(f"⚠️ Failed with {model_name}: {error_str.splitlines()[0]}...") # Log brief error
            last_error = e
            continue

    # If all models fail
    print(f"❌ All models failed. Last error: {last_error}")
    return f"I'm sorry, I am currently overloaded. Please check your API keys or try again later.", conversation_history or [], []
