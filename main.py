from __future__ import print_function

import uuid
import datetime
from datetime import datetime, timedelta
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
# Reading Data from Google API
# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
# CRUD Operations in Google API
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

        # Create Google Calender Event
        d = datetime.now().date()
        tomorrow = datetime(d.year, d.month, d.day, 10) + timedelta(days=1)
        start = tomorrow.isoformat()
        end = (tomorrow + timedelta(hours=1)).isoformat()

        event = {
            "summary": "Automating calendar",
            "description": "This is a tutorial example of automating google calendar with python",
            "colorId": 1,
            "conferenceData": {
                "createRequest": {
                    "requestId": "zz",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
            "start": {"dateTime": start, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end, "timeZone": "Asia/Kolkata"},
        }

        event_result = (
            service.events()
            .insert(
                calendarId="primary",
                sendNotifications=True,
                body=event,
                conferenceDataVersion=1,
            )
            .execute()
        )

        print("created event")
        print("id: ", event_result["id"])
        print("summary: ", event_result["summary"])
        print("starts at: ", event_result["start"]["dateTime"])
        print("ends at: ", event_result["end"]["dateTime"])

    except HttpError as error:
        print("An error occurred: %s" % error)


if __name__ == "__main__":
    main()
