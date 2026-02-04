"""
Agentic Brain: LLM Integration with Function Calling

This module sets up the OpenAI client with MCP tool definitions.
"""
import os
import json
from openai import OpenAI
from typing import Optional
from dotenv import load_dotenv

from tools.availability import check_availability
from tools.booking import book_appointment, cancel_appointment, list_appointments

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Tool definitions for OpenAI Function Calling
TOOLS = [
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
                        "description": "Optional: Filter by doctor specialization (general, cardiology, dermatology, neurology, orthopedics, pediatrics)",
                        "enum": ["general", "cardiology", "dermatology", "neurology", "orthopedics", "pediatrics"]
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
            "description": "Book an appointment with a doctor. Use this when the user wants to schedule or book a medical appointment.",
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

# Map function names to actual functions
TOOL_FUNCTIONS = {
    "check_availability": check_availability,
    "book_appointment": book_appointment,
    "cancel_appointment": cancel_appointment,
    "list_appointments": list_appointments
}

SYSTEM_PROMPT = """You are a helpful medical appointment assistant. You help patients:
1. Check doctor availability for specific dates
2. Book appointments with doctors
3. Cancel existing appointments
4. View their scheduled appointments

Be friendly and professional. When booking appointments:
- Always confirm the date and time with the user
- Ask for patient name and email if not provided
- Suggest available slots if the requested time is not available

For availability checks:
- If a specialization is mentioned, filter by that
- Present available slots in a clear, readable format

Today's date is the current date. Use this to validate appointment dates."""


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute a tool function and return the result."""
    if tool_name not in TOOL_FUNCTIONS:
        return {"error": f"Unknown tool: {tool_name}"}
    
    try:
        result = TOOL_FUNCTIONS[tool_name](**arguments)
        return result
    except Exception as e:
        return {"error": str(e)}


def chat(user_message: str, conversation_history: Optional[list] = None) -> tuple[str, list]:
    """
    Process a user message through the agentic loop.
    
    Args:
        user_message: The user's input message
        conversation_history: Optional list of previous messages
        
    Returns:
        Tuple of (assistant response, updated conversation history)
    """
    if conversation_history is None:
        conversation_history = []
    
    # Add system prompt if this is a new conversation
    if not conversation_history:
        conversation_history.append({
            "role": "system",
            "content": SYSTEM_PROMPT
        })
    
    # Add user message
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    # Call OpenAI with tools
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history,
        tools=TOOLS,
        tool_choice="auto"
    )
    
    assistant_message = response.choices[0].message
    
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
            
            print(f"   Result: {result}")
            
            # Add tool result to conversation
            conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
        
        # Get next response from the model
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            tools=TOOLS,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
    
    # Add final response to history
    final_response = assistant_message.content or ""
    conversation_history.append({
        "role": "assistant",
        "content": final_response
    })
    
    return final_response, conversation_history
