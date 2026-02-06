"""
Agentic Brain: LLM Integration with Function Calling

This module sets up the Groq client with MCP tool definitions.
Supports both patient and doctor roles with context-aware prompts.
"""
import os
import json
from datetime import date, datetime
from groq import Groq
from typing import Optional
from dotenv import load_dotenv

from tools.availability import check_availability
from tools.booking import book_appointment, cancel_appointment, list_appointments
from tools.doctor_reports import (
    get_appointment_stats,
    get_patient_stats,
    generate_summary_report,
    send_slack_notification,
    send_report_to_whatsapp
)
from tools.patient_history import (
    get_patient_history,
    add_visit_notes,
    add_prescription,
    generate_patient_report
)

load_dotenv()

# Initialize Groq client (free tier)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
            "name": "send_report_to_whatsapp",
            "description": "Generate and send a report to the doctor via WhatsApp. Use when doctor asks to send report to WhatsApp or their phone.",
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
    "check_availability": check_availability,
    "book_appointment": book_appointment,
    "cancel_appointment": cancel_appointment,
    "list_appointments": list_appointments,
    # Doctor tools
    "get_appointment_stats": get_appointment_stats,
    "get_patient_stats": get_patient_stats,
    "generate_summary_report": generate_summary_report,
    "send_slack_notification": send_slack_notification,
    "send_report_to_whatsapp": send_report_to_whatsapp,
    # Patient history tools
    "get_patient_history": get_patient_history,
    "add_visit_notes": add_visit_notes,
    "add_prescription": add_prescription,
    "generate_patient_report": generate_patient_report
}

# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

def get_system_prompt(role: str = "patient") -> str:
    """Get role-appropriate system prompt with current date context."""
    today = date.today()
    current_time = datetime.now().strftime("%H:%M")
    
    base_context = f"""Current Date: {today.strftime('%A, %B %d, %Y')}
Current Time: {current_time}
Today's date in YYYY-MM-DD format: {today.isoformat()}

Important date references:
- Today: {today.isoformat()}
- Tomorrow: {(today + __import__('datetime').timedelta(days=1)).isoformat()}
- Yesterday: {(today - __import__('datetime').timedelta(days=1)).isoformat()}
"""
    
    if role == "doctor":
        return f"""You are an intelligent medical assistant helping doctors manage their practice. You can:

1. **View Appointment Statistics**: Answer questions like "how many patients today?", "appointments this week"
2. **Query Patient Data**: Find patients by symptoms or diagnosis
3. **Generate Reports**: Create daily/weekly summary reports
4. **Send Notifications**: Send schedule summaries via Slack
5. **Manage Appointments**: Book, cancel, or view appointments

{base_context}

Guidelines:
- When asked about appointment counts, use get_appointment_stats
- For patient queries by symptoms (e.g., "patients with fever"), use get_patient_stats
- For summary reports, use generate_summary_report
- To send Slack notifications, use send_slack_notification with the doctor's ID
- Be concise and data-focused in responses
- Present statistics clearly and professionally

Available doctors in the system:
- ID 1: Dr. Sarah Johnson (General)
- ID 2: Dr. Michael Chen (Cardiology)
- ID 3: Dr. Emily Williams (Dermatology)
- ID 4: Dr. James Brown (Neurology)"""
    
    else:  # patient
        return f"""You are a friendly medical appointment assistant. Follow this EXACT flow with emoji formatting:

{base_context}

## BOOKING SEQUENCE (NEVER SKIP STEPS):

**STEP 1 - ASK FOR DOCTOR:**
User: "Book Appointment"
You: "👨‍⚕️ Which doctor would you like to see?\n\nAvailable doctors:\n• Dr. Mohit Adoni (General Practice) - ID: 5\n• Dr. Sarah Johnson (General Practice) - ID: 1\n• Dr. Michael Chen (Cardiology) - ID: 2\n• Dr. Emily Williams (Dermatology) - ID: 3\n• Dr. James Brown (Neurology) - ID: 4"
Then call list_doctors tool
WAIT for doctor selection

**STEP 2 - ASK FOR DATE:**
After doctor selected, ask: "📅 Which date works for you?\n\nYou can book for:\n• Tomorrow (Saturday, Feb 7)\n• Sunday, Feb 8"
WAIT for date

**STEP 3 - CHECK AVAILABILITY & SHOW SLOTS:**
After date selected, call check_availability(doctor_id, date)
Then show: "⏰ Available time slots for [Doctor] on [Date]:\n\n[list slots with bullets]\n\nWhat time works best for you?"
WAIT for time

**STEP 4 - ASK NAME:**
"👤 Great! What's your full name?"
WAIT

**STEP 5 - ASK EMAIL:**
"📧 What's your email address?"
WAIT

**STEP 6 - ASK REASON:**
"🏥 What brings you in today? (Your chief concern or symptoms)"
WAIT

**STEP 7 - CONFIRM:**
"✅ Please confirm your appointment:\n\n📋 **Appointment Details**\n• Doctor: [name]\n• Date: [date]\n• Time: [time]\n• Name: [name]\n• Email: [email]\n• Reason: [reason]\n\nIs this correct? (Yes/No)"
WAIT for "Yes"

**STEP 8 - BOOK & CONFIRM:**
Call book_appointment + send_email
Then: "🎉 **Appointment Confirmed!**\n\nYour appointment is booked with [Doctor] on [Date] at [Time].\n\n📧 Confirmation email sent to [email]\n📅 Calendar invite sent to the doctor\n\nIs there anything else I can help you with?"

## FORMATTING RULES:
- Use emojis for visual appeal (👨‍⚕️ 📅 ⏰ 📧 🏥 ✅ 🎉)
- Use bullet points with • for lists
- Use **bold** for important info
- Add line breaks for readability
- Keep responses clean and organized

## CRITICAL RULES:
- Ask for DATE BEFORE checking availability
- Never skip doctor or date selection
- One question at a time
- Wait for answer before proceeding

Doctor IDs: Mohit Adoni=5, Sarah Johnson=1, Michael Chen=2, Emily Williams=3, James Brown=4"""


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute a tool function and return the result."""
    if tool_name not in TOOL_FUNCTIONS:
        return {"error": f"Unknown tool: {tool_name}"}
    
    try:
        result = TOOL_FUNCTIONS[tool_name](**arguments)
        return result
    except Exception as e:
        return {"error": str(e)}


def chat(
    user_message: str,
    conversation_history: Optional[list] = None,
    role: str = "patient"
) -> tuple[str, list]:
    """
    Process a user message through the agentic loop.
    
    Args:
        user_message: The user's input message
        conversation_history: Optional list of previous messages
        role: User role - "patient" or "doctor"
        
    Returns:
        Tuple of (assistant response, updated conversation history)
    """
    if conversation_history is None:
        conversation_history = []
    
    # Select tools based on role
    tools = DOCTOR_TOOLS if role == "doctor" else PATIENT_TOOLS
    
    # Add system prompt if this is a new conversation
    if not conversation_history:
        conversation_history.append({
            "role": "system",
            "content": get_system_prompt(role)
        })
    
    # Add user message
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    # Call Groq with tools
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=conversation_history,
        tools=tools,
        tool_choice="auto"
    )
    
    assistant_message = response.choices[0].message
    tools_used = []
    
    # Check if the model wants to call tools
    while assistant_message.tool_calls:
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
            arguments = json.loads(tool_call.function.arguments)
            
            print(f"🔧 Executing tool: {function_name}")
            print(f"   Arguments: {arguments}")
            
            result = execute_tool(function_name, arguments)
            tools_used.append(function_name)
            
            print(f"   Result: {json.dumps(result, indent=2)[:500]}...")  # Truncate for logging
            
            # Add tool result to conversation
            conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
        
        # Get next response from the model
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=conversation_history,
            tools=tools,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
    
    # Add final response to history
    final_response = assistant_message.content or ""
    conversation_history.append({
        "role": "assistant",
        "content": final_response
    })
    
    # Log tools used for analytics
    if tools_used:
        print(f"📊 Tools used in this turn: {', '.join(tools_used)}")
    
    return final_response, conversation_history
