"""
Google Calendar API Integration Service.

Handles creating, updating, and deleting calendar events for appointments.
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Check if Google credentials are configured
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

# Flag to indicate if Google Calendar is configured
CALENDAR_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)


class GoogleCalendarService:
    """Service for interacting with Google Calendar API."""
    
    def __init__(self):
        self.calendar_id = GOOGLE_CALENDAR_ID
        self.service = None
        self._initialized = False
    
    def _get_service(self):
        """Get or create the Calendar API service."""
        if not CALENDAR_ENABLED:
            return None
        
        if self._initialized:
            return self.service
        
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request
            import pickle
            
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            creds = None
            
            # Load saved credentials
            token_path = os.path.join(os.path.dirname(__file__), '..', 'token.pickle')
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # For initial setup, credentials need to be obtained via OAuth flow
                    print("⚠️ Google Calendar credentials not found. Run setup_google_auth.py first.")
                    return None
                
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('calendar', 'v3', credentials=creds)
            self._initialized = True
            return self.service
            
        except Exception as e:
            print(f"⚠️ Failed to initialize Google Calendar: {e}")
            return None
    
    def create_event(
        self,
        summary: str,
        description: str,
        start_datetime: datetime,
        end_datetime: datetime,
        attendee_email: Optional[str] = None,
        calendar_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a calendar event for an appointment.
        
        Args:
            summary: Event title (e.g., "Appointment with Dr. Smith")
            description: Event description with details
            start_datetime: Start time of the appointment
            end_datetime: End time of the appointment
            attendee_email: Patient's email to send invite
            calendar_id: Optional specific calendar ID
            
        Returns:
            Dict with event_id on success or error message
        """
        service = self._get_service()
        if not service:
            return {
                "success": False,
                "error": "Google Calendar not configured",
                "event_id": None
            }
        
        try:
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'Asia/Kolkata',  # IST timezone
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 30},  # 30 mins before
                    ],
                },
            }
            
            if attendee_email:
                event['attendees'] = [{'email': attendee_email}]
            
            created_event = service.events().insert(
                calendarId=calendar_id or self.calendar_id,
                body=event,
                sendUpdates='all' if attendee_email else 'none'
            ).execute()
            
            return {
                "success": True,
                "event_id": created_event.get('id'),
                "html_link": created_event.get('htmlLink')
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "event_id": None
            }
    
    def delete_event(self, event_id: str, calendar_id: Optional[str] = None) -> Dict[str, Any]:
        """Delete a calendar event."""
        service = self._get_service()
        if not service:
            return {"success": False, "error": "Google Calendar not configured"}
        
        try:
            service.events().delete(
                calendarId=calendar_id or self.calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            return {"success": True, "message": "Event deleted"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_events(
        self,
        start_date: datetime,
        end_date: datetime,
        calendar_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get events within a date range."""
        service = self._get_service()
        if not service:
            return {"success": False, "error": "Google Calendar not configured", "events": []}
        
        try:
            events_result = service.events().list(
                calendarId=calendar_id or self.calendar_id,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return {
                "success": True,
                "events": events,
                "count": len(events)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "events": []}


# Singleton instance
calendar_service = GoogleCalendarService()


def create_appointment_event(
    doctor_name: str,
    patient_name: str,
    patient_email: str,
    appointment_date: str,
    appointment_time: str,
    reason: str = "Medical Appointment",
    duration_minutes: int = 30
) -> Dict[str, Any]:
    """
    Convenience function to create a calendar event for an appointment.
    
    Returns:
        Dict with event_id on success or error
    """
    try:
        from datetime import datetime
        
        start_dt = datetime.strptime(
            f"{appointment_date} {appointment_time}",
            "%Y-%m-%d %H:%M"
        )
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        summary = f"Medical Appointment - {patient_name} with {doctor_name}"
        description = f"""
Appointment Details:
- Patient: {patient_name}
- Doctor: {doctor_name}
- Reason: {reason}
- Date: {appointment_date}
- Time: {appointment_time}

Please arrive 10 minutes early for check-in.
        """.strip()
        
        return calendar_service.create_event(
            summary=summary,
            description=description,
            start_datetime=start_dt,
            end_datetime=end_dt,
            attendee_email=patient_email
        )
        
    except Exception as e:
        return {"success": False, "error": str(e), "event_id": None}
