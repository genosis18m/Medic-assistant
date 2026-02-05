"""
Slack Notification Service for Doctor Reports.

Sends formatted notifications to doctors via Slack webhooks.
"""
import os
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Check if Slack is configured
SLACK_ENABLED = bool(SLACK_WEBHOOK_URL)


async def send_slack_message(
    message: str,
    blocks: Optional[List[Dict]] = None,
    webhook_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a message to Slack via webhook.
    
    Args:
        message: Plain text message (fallback)
        blocks: Optional Slack Block Kit blocks for rich formatting
        webhook_url: Optional specific webhook URL
        
    Returns:
        Dict with success status
    """
    url = webhook_url or SLACK_WEBHOOK_URL
    
    if not url:
        print("⚠️ Slack webhook not configured. Skipping notification.")
        return {
            "success": False,
            "error": "Slack not configured",
            "skipped": True
        }
    
    payload = {"text": message}
    if blocks:
        payload["blocks"] = blocks
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                print("✅ Slack notification sent")
                return {"success": True, "message": "Notification sent"}
            else:
                return {
                    "success": False,
                    "error": f"Slack returned {response.status_code}: {response.text}"
                }
                
    except Exception as e:
        print(f"❌ Failed to send Slack notification: {e}")
        return {"success": False, "error": str(e)}


def send_slack_message_sync(
    message: str,
    blocks: Optional[List[Dict]] = None,
    webhook_url: Optional[str] = None
) -> Dict[str, Any]:
    """Synchronous version of send_slack_message."""
    url = webhook_url or SLACK_WEBHOOK_URL
    
    if not url:
        return {
            "success": False,
            "error": "Slack not configured",
            "skipped": True
        }
    
    payload = {"text": message}
    if blocks:
        payload["blocks"] = blocks
    
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload)
            
            if response.status_code == 200:
                return {"success": True, "message": "Notification sent"}
            else:
                return {
                    "success": False,
                    "error": f"Slack returned {response.status_code}"
                }
                
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_daily_summary_blocks(
    doctor_name: str,
    date_str: str,
    total_appointments: int,
    completed: int,
    pending: int,
    cancelled: int,
    appointments: List[Dict]
) -> List[Dict]:
    """
    Create Slack Block Kit blocks for a daily summary report.
    """
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📊 Daily Summary Report - {date_str}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Doctor:* {doctor_name}"
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*📋 Total Appointments:*\n{total_appointments}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*✅ Completed:*\n{completed}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*⏳ Pending:*\n{pending}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*❌ Cancelled:*\n{cancelled}"
                }
            ]
        }
    ]
    
    # Add appointment list if there are appointments
    if appointments:
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📅 Appointment Details:*"
            }
        })
        
        for apt in appointments[:10]:  # Limit to 10 to avoid message size limits
            status_emoji = {
                "confirmed": "🟢",
                "pending": "🟡",
                "completed": "✅",
                "cancelled": "🔴",
                "no_show": "⚫"
            }.get(apt.get("status", "pending"), "⚪")
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{status_emoji} *{apt.get('time', 'N/A')}* - {apt.get('patient', 'Unknown')}\n_{apt.get('reason', 'General checkup')}_"
                }
            })
    
    # Add footer
    blocks.append({"type": "divider"})
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Generated by Medical Assistant at {datetime.now().strftime('%H:%M:%S')}"
            }
        ]
    })
    
    return blocks


def send_doctor_summary_report(
    doctor_name: str,
    date_str: str,
    stats: Dict[str, Any],
    appointments: List[Dict]
) -> Dict[str, Any]:
    """
    Send a formatted summary report to the doctor via Slack.
    """
    blocks = create_daily_summary_blocks(
        doctor_name=doctor_name,
        date_str=date_str,
        total_appointments=stats.get("total", 0),
        completed=stats.get("completed", 0),
        pending=stats.get("pending", 0),
        cancelled=stats.get("cancelled", 0),
        appointments=appointments
    )
    
    fallback_message = f"Daily Summary for {doctor_name} on {date_str}: {stats.get('total', 0)} appointments"
    
    return send_slack_message_sync(fallback_message, blocks)


def send_new_appointment_notification(
    doctor_name: str,
    patient_name: str,
    appointment_date: str,
    appointment_time: str,
    reason: str
) -> Dict[str, Any]:
    """
    Send a notification when a new appointment is booked.
    """
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📅 New Appointment Booked",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Doctor:*\n{doctor_name}"},
                {"type": "mrkdwn", "text": f"*Patient:*\n{patient_name}"},
                {"type": "mrkdwn", "text": f"*Date:*\n{appointment_date}"},
                {"type": "mrkdwn", "text": f"*Time:*\n{appointment_time}"}
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Reason:* {reason}"
            }
        }
    ]
    
    fallback = f"New appointment: {patient_name} with {doctor_name} on {appointment_date} at {appointment_time}"
    
    return send_slack_message_sync(fallback, blocks)
