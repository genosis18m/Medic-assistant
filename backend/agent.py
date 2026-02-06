"""
Agentic Brain: LLM Integration with Function Calling

This module sets up the Groq client with MCP tool definitions.
Supports both patient and doctor roles with context-aware prompts.
"""
import os
import json
from datetime import date, datetime
from groq import Groq
from typing import Optional, Dict, Any
from dotenv import load_dotenv

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

# Initialize Groq client (free tier)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#By default the Groq client uses headers that might be incompatible with certain proxies or environments if not configured well.
# Ensure environment variables are loaded.

# ============================================================================
# TOOL DEFINITIONS FOR FUNCTION CALLING
# ============================================================================

# Patient-facing tools
PATIENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_doctors",
            "description": "List all available doctors with their IDs, names, and specializations. Use this when user asks about doctors or when starting the booking process.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check available appointment slots for doctors on a specific date. Use this when the user asks about available times or wants to see when a doctor is free.",
            "parameters": {
                "type": "object",
                "properties": {
                    "check_date": {
                        "type": "string",
                        "description": "The date to check availability for in YYYY-MM-DD format"
                    },
                    "specialization": {
                        "type": "string",
                        "description": "Optional: Filter by doctor specialization (general, cardiology, dermatology, neurology, orthopedics, pediatrics). Leave empty if not filtering."
                    },
                    "doctor_id": {
                        "type": "integer",
                        "description": "Optional: Specific doctor ID to check"
                    }
                },
                "required": ["check_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment with a doctor. Use this when the user wants to schedule or book a medical appointment. Automatically sends email confirmation and creates calendar event.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_id": {
                        "type": "integer",
                        "description": "The ID of the doctor to book with"
                    },
                    "patient_name": {
                        "type": "string",
                        "description": "Full name of the patient"
                    },
                    "patient_email": {
                        "type": "string",
                        "description": "Email address of the patient"
                    },
                    "appointment_date": {
                        "type": "string",
                        "description": "The date for the appointment in YYYY-MM-DD format"
                    },
                    "appointment_time": {
                        "type": "string",
                        "description": "The time for the appointment in HH:MM format (24-hour)"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the appointment (e.g., 'Annual checkup', 'Headache')"
                    },
                    "symptoms": {
                        "type": "string",
                        "description": "Optional: Comma-separated list of symptoms"
                    }
                },
                "required": ["doctor_id", "patient_name", "patient_email", "appointment_date", "appointment_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment. Use this when the user wants to cancel their appointment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": "The ID of the appointment to cancel"
                    }
                },
                "required": ["appointment_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_appointments",
            "description": "List all appointments, optionally filtered by patient email. Use this to see existing appointments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_email": {
                        "type": "string",
                        "description": "Optional: Filter appointments by patient email"
                    }
                },
                "required": []
            }
        }
    }
]

# Doctor-facing tools (includes patient tools + reporting)
DOCTOR_TOOLS = PATIENT_TOOLS + [
    {
        "type": "function",
        "function": {
            "name": "get_appointment_stats",
            "description": "Get appointment statistics for a date or date range. Use for queries like 'how many patients today', 'appointments this week', etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_id": {
                        "type": "integer",
                        "description": "Optional: Specific doctor ID to get stats for"
                    },
                    "date_str": {
                        "type": "string",
                        "description": "Single date in YYYY-MM-DD format (e.g., for 'today' or 'yesterday')"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start of date range in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End of date range in YYYY-MM-DD format"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_patient_stats",
            "description": "Get patient statistics filtered by symptoms or diagnosis. Use for queries like 'how many patients with fever', 'patients with headache this week', etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symptoms": {
                        "type": "string",
                        "description": "Symptoms to search for (e.g., 'fever', 'headache', 'cough')"
                    },
                    "diagnosis": {
                        "type": "string",
                        "description": "Diagnosis to search for"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start of date range in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End of date range in YYYY-MM-DD format"
                    },
                    "doctor_id": {
                        "type": "integer",
                        "description": "Optional: Filter by specific doctor"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_summary_report",
            "description": "Generate a comprehensive summary report. Use when doctor asks for daily/weekly summary or wants a report sent to them.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_id": {
                        "type": "integer",
                        "description": "ID of the doctor to generate report for"
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Type of report: 'daily' or 'weekly'",
                        "enum": ["daily", "weekly"]
                    },
                    "date_str": {
                        "type": "string",
                        "description": "Specific date for the report in YYYY-MM-DD format"
                    },
                    "send_notification": {
                        "type": "boolean",
                        "description": "Whether to send the report via Slack notification"
                    }
                },
                "required": ["doctor_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_slack_notification",
            "description": "Send a notification or summary to the doctor via Slack. Use when doctor wants to receive their schedule or report on Slack.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_id": {
                        "type": "integer",
                        "description": "ID of the doctor"
                    },
                    "message": {
                        "type": "string",
                        "description": "Optional custom message to include"
                    },
                    "include_today_summary": {
                        "type": "boolean",
                        "description": "Whether to include today's appointment summary (default: true)"
                    }
                },
                "required": ["doctor_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_report_to_telegram",
            "description": "Generate a PDF report and send it to the doctor via Telegram. Use when doctor asks to send report to Telegram.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_id": {
                        "type": "integer",
                        "description": "ID of the doctor"
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Type of report: 'daily' or 'weekly'",
                        "enum": ["daily", "weekly"]
                    },
                    "date_str": {
                        "type": "string",
                        "description": "Specific date for the report in YYYY-MM-DD format"
                    },
                    "chat_id": {
                        "type": "string",
                        "description": "Optional: Telegram chat ID if known."
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "Optional: Doctor's phone number to send report to (if chat ID unknown)."
                    }
                },
                "required": ["doctor_id"]
            }
        }
    }
]

# Map function names to actual functions
TOOL_FUNCTIONS = {
    # Patient tools
    "list_doctors": list_doctors,
    "check_availability": check_availability,
    "book_appointment": book_appointment,
    "cancel_appointment": cancel_appointment,
    "list_appointments": list_appointments,
    # Doctor tools
    "get_appointment_stats": get_appointment_stats,
    "get_patient_stats": get_patient_stats,
    "generate_summary_report": generate_summary_report,
    "send_slack_notification": send_slack_notification,
    "send_report_to_telegram": send_report_to_telegram,
    # Patient history tools
    "get_patient_history": get_patient_history,
    "add_visit_notes": add_visit_notes,
    "add_prescription": add_prescription,
    "generate_patient_report": generate_patient_report
}

# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

def get_system_prompt(role: str = "patient", context: str = "") -> str:
    """Get role-appropriate system prompt with current date context."""
    today = date.today()
    current_time = datetime.now().strftime("%H:%M")
    
    base_context = f"""Current Date: {today.strftime('%A, %B %d, %Y')}
Current Time: {current_time}
Today's date in YYYY-MM-DD format: {today.isoformat()}
{context}

Important date references:
- Today: {today.isoformat()}
- Tomorrow: {(today + __import__('datetime').timedelta(days=1)).isoformat()}
- Yesterday: {(today - __import__('datetime').timedelta(days=1)).isoformat()}
"""
    
    if role == "doctor":
        return f"""You are an intelligent medical assistant helping doctors manage their practice. 

CRITICAL: You are integrating with a function calling API. You must use the native 'tool_calls' feature for any actions. Do not output text descriptions of functions or XML tags. Use strictly valid JSON for arguments.

You can:
1. **View Appointment Statistics**: Answer questions like "how many patients today?", "appointments this week"
2. **Query Patient Data**: Find patients by symptoms or diagnosis
3. **Generate Reports**: Create daily/weekly summary reports
4. **Send Notifications**: Send schedule summaries via Slack or Telegram
5. **Manage Appointments**: Book, cancel, or view appointments

{base_context}

Guidelines:
- **CRITICAL**: For ALL tool calls requiring `doctor_id`, **YOU MUST USE THE ID FROM THE CONTEXT ABOVE**.
- **REPORTING**: When asked for "Weekly Report", "Send Report", or "Telegram Report":
  - **ALWAYS** call `send_report_to_telegram`.
  - **ALWAYS** pass the `phone_number` from the context if available (e.g. "9876543210").
  - **ALWAYS** call `send_report_to_telegram`.
  - **ALWAYS** pass the `phone_number` from the context if available (e.g. "9876543210").
  - Do NOT just write a text summary unless specifically asked for "text only".
  - **NEVER** output raw Python code or tags like `<|python_tag|>`. Use the provided JSON tool interface ONLY.
- **Self-Correction**: If the user asks for a report and you didn't call the tool, apologize and call it immediately.
- Never default to ID 1 unless specified.
- When asked about "my schedule", "my appointments", or "what is tomorrow's schedule", ALWAYS use `generate_summary_report` or `get_appointment_stats` for the CURRENT Doctor ID.
- DO NOT use `check_availability` for doctor queries about their own schedule (that is for booking new patients).
- For patient queries by symptoms (e.g., "patients with fever"), use get_patient_stats
- Be concise and data-focused in responses

Available doctors in the system:
- ID 1: Dr. Sarah Johnson (General)
- ID 2: Dr. Michael Chen (Cardiology)
- ID 3: Dr. Emily Williams (Dermatology)
- ID 4: Dr. James Brown (Neurology)
- ID 5: Dr. Mohit Adoni (General)"""
    
    else:  # patient
        return f"""You are a friendly medical appointment assistant.
        
{base_context}

## YOUR GOAL
Help patients book appointments by gathering 3 key pieces of info:
1. **Date** (and Time)
2. **Doctor**
3. **Reason** (and Name/Email if missing)

## CRITICAL INSTRUCTIONS
1. **TOOL CALLING**: You must use the NATIVE `tool_calls` feature.
   - ❌ DO NOT output text like `<function=check_availability>...`
   - ❌ DO NOT output JSON in markdown blocks.
   - ✅ JUST CALL THE TOOL directly.

2. **ONE STEP AT A TIME**: Do not ask for everything at once.

## BOOKING FLOW
1. **Greeting**: Ask how you can help.
2. **Date**: If user says "Book appointment", ask "When would you like to come in?"
   - Suggest: "Tomorrow" or specific dates.
3. **Doctor**: Ask "Which doctor would you like to see?". Call `list_doctors` to show options.
4. **Availability**: Once you have Doctor + Date -> CALL `check_availability(doctor_id, check_date)`.
   - Then show the list of available slots.
5. **Details**: Ask for Name, Email, Reason (if not already known).
6. **Book**: CALL `book_appointment`.

## IMPORTANT RULES
- **If you need to check availability, call the tool IMMEDIATELY.** Do not say you are going to do it, just do it.
- **Suggestions**: End every turn with a suggested reply for the user in this format:
  `[[SUGGESTIONS: Option 1, Option 2, Option 3]]`

Doctor IDs: Mohit Adoni=5, Sarah Johnson=1, Michael Chen=2, Emily Williams=3, James Brown=4"""


import inspect

async def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute a tool function and return the result."""
    if tool_name not in TOOL_FUNCTIONS:
        return {"error": f"Unknown tool: {tool_name}"}
    
    try:
        func = TOOL_FUNCTIONS[tool_name]
        if inspect.iscoroutinefunction(func):
            result = await func(**arguments)
        else:
            result = func(**arguments)
        return result
    except Exception as e:
        return {"error": str(e)}


async def chat(
    user_message: str,
    conversation_history: Optional[list] = None,
    role: str = "patient",
    user_context: str = ""
) -> tuple[str, list, list]:
    """
    Process a user message through the agentic loop.
    
    Args:
        user_message: The user's input message
        conversation_history: Optional list of previous messages
        role: User role - "patient" or "doctor"
        user_context: Optional context string (e.g., "You are Dr. X")
        
    Returns:
        Tuple of (assistant response, updated conversation history, suggested actions)
    """
    if conversation_history is None:
        conversation_history = []
    
    # Select tools based on role
    tools = DOCTOR_TOOLS if role == "doctor" else PATIENT_TOOLS
    
    # Add system prompt if this is a new conversation
    if not conversation_history:
        conversation_history.append({
            "role": "system",
            "content": get_system_prompt(role, user_context)
        })
    
    # Add user message
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    suggested_actions = []

    try:
        # Call Groq with tools
        # Note: Using sync client in async func blocks loop, but fine for prototype
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation_history,
            tools=tools,
            tool_choice="auto"
        )
        
        print(f"🤖 Raw LLM Response: {response.choices[0].message.content}")
        print(f"🛠️ Tool Calls: {response.choices[0].message.tool_calls}")
        
        assistant_message = response.choices[0].message
        final_response_content = assistant_message.content or ""
        tools_used = []
        
        # ---------------------------------------------------------
        # ROBUST TOOL PARSING: Handle standard tool_calls AND XML hallucinations
        # ---------------------------------------------------------
        
        # 1. Standard Tool Calls (Native)
        if assistant_message.tool_calls:
            # Add assistant's tool call request to history
            conversation_history.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })
            
            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                
                print(f"🔧 Executing tool (Native): {function_name}")
                result = await execute_tool(function_name, arguments)
                tools_used.append(function_name)
                
                conversation_history.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result)
                })

        # 2. XML Hallucination Fallback (<function=name>args</function>)
        elif "<function=" in final_response_content or "<|python_tag|>" in final_response_content:
            import re
            print(f"⚠️ XML/Tag Hallucination detected in: {final_response_content[:50]}...")
            
            # Pattern 1: <function=name>args</function>
            xml_matches = re.finditer(r'<function=(\w+)>(.*?)</function>', final_response_content, re.DOTALL)
            
            # Pattern 2: <|python_tag|>call_tool(name="foo", args={...})  <-- harder to parse generally, focusing on specific leak
            # Often Llama 3 leaks: <|python_tag|>send_report_to_telegram(doctor_id=2, report_type='weekly')
            
            # Simple parser for the specific leak user reported
            if "<|python_tag|>" in final_response_content:
                # Naive attempt to extract function name and args from a python-like string
                # This is a fallback hack to save the interaction
                code_content = final_response_content.split("<|python_tag|>")[1].strip()
                # Try to capture function name:  name(
                func_match = re.match(r'^(\w+)\s*\(', code_content)
                if func_match:
                    func_name = func_match.group(1)
                    # Try to parse arguments. This is tricky without a real python parser.
                    # We will assume JSON-like kwargs or similiar.
                    # HACK: If it's `send_report_to_telegram`, we can try to extract known args via Regex
                    if func_name == "send_report_to_telegram":
                        args = {}
                        # Extract doctor_id
                        d_id_match = re.search(r'doctor_id\s*=\s*(\d+)', code_content)
                        if d_id_match: args['doctor_id'] = int(d_id_match.group(1))
                        
                        # Extract report_type
                        r_type_match = re.search(r'report_type=[\'"](\w+)[\'"]', code_content)
                        if r_type_match: args['report_type'] = r_type_match.group(1)
                        
                        # Extract phone/chat from context (better to just default if regex fails)
                        # Let's rely on self-correction mostly, but this catches the basic leak
                        
                        if args:
                            print(f"🔧 Executing tool (Python Tag Rescue): {func_name} with {args}")
                            result = await execute_tool(func_name, args)
                            tools_used.append(func_name)
                            conversation_history.append({
                                "role": "system", 
                                "content": f"Tool '{func_name}' executed via fallback parser. Result: {json.dumps(result)}"
                            })
                            # Clean the leaked tag from the response shown to user
                            final_response_content = final_response_content.split("<|python_tag|>")[0].strip()

            for match in xml_matches:
                found_xml_tools = True
                func_name = match.group(1)
                args_str = match.group(2).strip()
                
                # Try to parse args as JSON, or key=value fallback
                try:
                    # Clean potential markdown wrapping around JSON
                    if args_str.startswith("```json"):
                        args_str = args_str.replace("```json", "").replace("```", "").strip()
                    elif args_str.startswith("`"):
                        args_str = args_str.strip("`")
                        
                    # Handle "check_date=2026-02-07" style
                    if "=" in args_str and "{" not in args_str:
                         # Simple key-value pair conversion
                         parts = args_str.split("=")
                         if len(parts) == 2:
                             args = {parts[0].strip(): parts[1].strip()}
                         else:
                             args = {} # Too complex to parse blindly
                    else:
                        args = json.loads(args_str)
                except:
                    print(f"⚠️ Failed to parse keys from: {args_str}, trying raw dict")
                    args = {} 
                
                print(f"🔧 Executing tool (XML Fallback): {func_name} with {args}")
                result = await execute_tool(func_name, args)
                tools_used.append(func_name)
                
                # We need to simulate a tool cycle for the history to make sense to the model
                # Append the "assistant" message that *would* have called this
                conversation_history.append({
                    "role": "assistant",
                    "content": final_response_content
                })
                
                # Append the function result disguised as a system or user confirmation 
                # (since we can't inject a 'tool' role without a real 'tool_call_id')
                conversation_history.append({
                    "role": "system",
                    "content": f"Function '{func_name}' executed. Result: {json.dumps(result)}"
                })
        
        # ---------------------------------------------------------
        # Get next response if tools were used
        # ---------------------------------------------------------
        if tools_used:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=conversation_history,
                tools=tools,
                tool_choice="auto"
            )
            assistant_message = response.choices[0].message
            final_response_content = assistant_message.content or ""
        
        # Parse suggestions from response (Format: [[SUGGESTIONS: Option 1, Option 2]])
        import re
        suggestion_match = re.search(r'\[\[SUGGESTIONS: (.*?)\]\]', final_response_content, re.DOTALL)
        if suggestion_match:
            suggestion_str = suggestion_match.group(1)
            suggested_actions = [s.strip() for s in suggestion_str.split(',')]
            # Remove the suggestion block from the user-facing message
            final_response_content = final_response_content.replace(suggestion_match.group(0), "").strip()
            
        conversation_history.append({
            "role": "assistant",
            "content": final_response_content # Store clean content
        })
        
        if tools_used:
             print(f"📊 Tools used: {', '.join(tools_used)}")
             
        # Detect if we need special client-side suggestions (e.g. time slots from text)
        # Fallback if LLM didn't provide them but context implies
        if not suggested_actions:
            lower_resp = final_response_content.lower()
            if "available time slots" in lower_resp and ":" in lower_resp:
                # Let client regex handle it OR try to parse here
                 pass 

        return final_response_content, conversation_history, suggested_actions

    except Exception as e:
        # Retry logic for tool use failures (common with Groq/Llama3)
        error_str = str(e)
        from groq import BadRequestError
        
        # Check if we have the failed generation content to rescue
        failed_content = ""
        if isinstance(e, BadRequestError) and hasattr(e, 'body') and 'failed_generation' in e.body.get('error', {}):
             failed_content = e.body['error']['failed_generation']
        
        if failed_content:
            print(f"🚑 Rescuing failed generation: {failed_content[:100]}...")
            # Reuse the parsing logic from above (simulated)
            import re
             # Pattern 1: <function=name>args</function>
            xml_matches = re.finditer(r'<function=(\w+)>(.*?)</function>', failed_content, re.DOTALL)
            
            rescued_tools = []
            
            for match in xml_matches:
                func_name = match.group(1)
                args_str = match.group(2).strip()
                try:
                    if args_str.startswith("```json"):
                        args_str = args_str.replace("```json", "").replace("```", "").strip()
                    elif args_str.startswith("`"):
                        args_str = args_str.strip("`")
                    
                    if "=" in args_str and "{" not in args_str:
                         parts = args_str.split("=")
                         if len(parts) == 2:
                             args = {parts[0].strip(): parts[1].strip()}
                         else:
                             args = {}
                    else:
                        args = json.loads(args_str)
                except:
                    args = {} 
                
                print(f"🔧 Executing tool (Rescue): {func_name}")
                result = await execute_tool(func_name, args)
                rescued_tools.append(result)
                
                conversation_history.append({
                    "role": "assistant",
                    "content": failed_content
                })
                conversation_history.append({
                    "role": "system", 
                    "content": f"Tool '{func_name}' executed. Result: {json.dumps(result)}"
                })
            
            # Pattern 2: Python Tag Rescue
            if "<|python_tag|>" in failed_content:
                try:
                    code_content = failed_content.split("<|python_tag|>")[1].strip()
                    func_match = re.match(r'^(\w+)\s*\(', code_content)
                    if func_match:
                        func_name = func_match.group(1)
                        if func_name == "send_report_to_telegram":
                            args = {}
                            d_id_match = re.search(r'doctor_id\s*=\s*(\d+)', code_content)
                            if d_id_match: args['doctor_id'] = int(d_id_match.group(1))
                            r_type_match = re.search(r'report_type=[\'"](\w+)[\'"]', code_content)
                            if r_type_match: args['report_type'] = r_type_match.group(1)
                            
                            if args:
                                print(f"🔧 Executing tool (Rescue Python): {func_name}")
                                result = await execute_tool(func_name, args)
                                rescued_tools.append(result)
                                conversation_history.append({
                                    "role": "system", 
                                    "content": f"Tool '{func_name}' executed via rescue. Result: {json.dumps(result)}"
                                })
                except Exception as rescue_e:
                    print(f"⚠️ Rescue failed: {rescue_e}")

            if rescued_tools:
                # If we rescued something, recursively call chat or just return success message
                # Simpler: Return a success message based on the result
                final_msg = "I have successfully executed the requested action."
                conversation_history.append({"role": "assistant", "content": final_msg})
                return final_msg, conversation_history, []

        # Fallback to standard retry if no failed_generation or rescue failed
        if "tool_use_failed" in error_str or "400" in error_str:
            print(f"⚠️ Tool use failed, retrying with correction... Error: {error_str}")
            try:
                # Add a system correction message
                conversation_history.append({
                    "role": "system",
                    "content": "Measurements indicate you attempted to use invalid tool syntax (e.g. XML). You MUST use the native 'tool_calls' JSON format. Please try again."
                })
                
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=conversation_history,
                    tools=tools,
                    tool_choice="auto"
                )
                
                assistant_message = response.choices[0].message
                if assistant_message.tool_calls:
                     # ... (Existing retry logic) ...
                     # Simplified for brevity: just return text if no tool calls this time
                    return assistant_message.content or "Please try again.", conversation_history, []
                else:
                    return assistant_message.content, conversation_history, []

            except Exception as retry_e:
                print(f"❌ Retry failed: {retry_e}")
        
        import traceback
        traceback.print_exc()
        error_msg = f"😕 I encountered an internal error: {str(e)}. Please try again."
        return error_msg, conversation_history, []
