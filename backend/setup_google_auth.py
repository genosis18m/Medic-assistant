from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import os

# Scopes required for Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    print("🔐 Starting Google Calendar Authentication Setup...")
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ Error: 'credentials.json' not found in the current directory.")
        print("   Please download your OAuth 2.0 Client credentials from Google Cloud Console")
        print("   and save them as 'credentials.json' in this folder.")
        return

    try:
        # Create the flow using the client secrets file
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)

        # Run the local server to authorize
        # IMPORTANT: Port 8080 must match the 'Authorized redirect URI' in Google Console
        # i.e., http://localhost:8080/
        print("🌐 Opening browser for authentication...")
        creds = flow.run_local_server(port=8080)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        print("✅ Authentication successful!")
        print("📄 'token.pickle' file created. The backend can now access Google Calendar.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == '__main__':
    main()
