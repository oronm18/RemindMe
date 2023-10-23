"""
FastAPI server module.
Author: Oron Moshe
Date: 22/10/2023
"""
# ----- Imports ----- #

import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import uvicorn
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request

from common.handlers.server_handler import CombinedHandler
from core.user import UserDoesNotExist

# ----- FastAPI server ----- #

app = FastAPI()
router = APIRouter()


class RateLimiter:
    def __init__(self, requests: int, window: int):
        """
        :param requests: Number of allowed requests
        :param window: Time window in seconds
        """
        self.requests = requests
        self.window = window
        self.timestamps = {}

    def request(self, client: str) -> bool:
        """
        Check and register the request for rate limiting.

        :param client: Client identifier (e.g. IP address)
        :return: True if request is allowed, False otherwise
        """
        now = time.time()
        if client not in self.timestamps:
            self.timestamps[client] = []

        self.timestamps[client] = [
            ts for ts in self.timestamps[client] if ts > now - self.window
        ]

        if len(self.timestamps[client]) < self.requests:
            self.timestamps[client].append(now)
            return True

        return False


rate_limiter = RateLimiter(requests=50, window=60)  # 50 requests per minute


def rate_limit(request: Request):
    client_ip = request.client.host
    if not rate_limiter.request(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests")
    return True


def get_handler():
    return CombinedHandler()


# ----- Routs ----- #

@router.post("/login/", dependencies=[Depends(rate_limit)])
def add_user(
        username: str,
        password: str,
        handler: CombinedHandler = Depends(get_handler)):
    try:
        user_id = handler.users_handler.login(username, password)
        return {"status": "success", "user_id": user_id}
    except UserDoesNotExist:
        raise HTTPException(status_code=400, detail="Username does not exist.")
    except ValueError:  # Raised for incorrect password
        raise HTTPException(status_code=401, detail="Incorrect password.")
    except Exception as e:  # Catch all other exceptions
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register/", dependencies=[Depends(rate_limit)])
def register(
        username: str,
        mail: str,
        password: str,
        handler: CombinedHandler = Depends(get_handler)):
    return {"user_id": handler.add_user(username, mail, password)}


@router.get("/get_user/{user_id}/", dependencies=[Depends(rate_limit)])
def get_user(user_id: str, handler: CombinedHandler = Depends(get_handler)):
    return handler.get_user(user_id)


@router.delete("/remove_user/{user_id}/", dependencies=[Depends(rate_limit)])
def remove_user(user_id: str, handler: CombinedHandler = Depends(get_handler)):
    handler.remove_user(user_id)
    return {"message": "User removed successfully"}


@router.post("/schedule_event/", dependencies=[Depends(rate_limit)])
def schedule_event(
        user_id: str,
        name: str,
        description: str,
        location: str,
        start: datetime,
        end: datetime = None,
        handler: CombinedHandler = Depends(get_handler)):
    return {"event_id": handler.add_event(user_id,
                                          name,
                                          description,
                                          location,
                                          [],
                                          start,
                                          end)}


@router.delete("/remove_event/{event_name}/", dependencies=[Depends(rate_limit)])
def remove_event(user_id: str, event_name: str, handler: CombinedHandler = Depends(get_handler)):
    event = handler.get_events_by_attribute(event_name=event_name)[0]
    if event.created_user_id != user_id:
        raise Exception("Only the user who created this event can remove it. Invalid user id.")
    handler.remove_event(event.event_id)
    handler.send_message(event.event_id, "The event is cancelled.")
    return {"message": "Event removed successfully"}


@router.put("/modify_event/{event_name}/", dependencies=[Depends(rate_limit)])
def modify_event(
        user_id: str,
        event_name: str,
        name: str = None,
        description: str = None,
        location: str = None,
        start: datetime = None,
        end: datetime = None,
        handler: CombinedHandler = Depends(get_handler)
):
    event = handler.get_events_by_attribute(event_name=event_name)[0]
    if event.created_user_id != user_id:
        raise Exception("Only the user who created this event can modify it. Invalid user id.")

    changes = {}
    if name: changes["event_name"] = name
    if description: changes["event_description"] = description
    if location: changes["location"] = location
    if start: changes["event_start_time"] = start
    if end: changes["event_end_time"] = end
    handler.modify_event(event.event_id, **changes)

    # Update all the users who invited.
    handler.send_message(event.event_id, "The event have been modify. please check this out.")
    return {"message": "Event modified successfully"}


@router.get("/events", dependencies=[Depends(rate_limit)])
def get_events_by_attribute(
        sort_by_attribute: str = None,  # Event
        reverse: bool = False,
        location: Optional[str] = None,
        handler: CombinedHandler = Depends(get_handler)
):
    events = handler.get_events_by_attribute(sort_by_attribute, reverse, location_filter=location)
    users = []
    for event in events:
        for subscriber_id in event.subscribers:
            users.append(handler.get_user(subscriber_id).user_name)
        event.subscribers = list(users)
        users = []
    return events


@router.get("/get_event/{event_name}/", dependencies=[Depends(rate_limit)])
def get_event(event_name: str, handler: CombinedHandler = Depends(get_handler)):
    event = handler.get_events_by_attribute(event_name=event_name)
    if len(event) != 1:
        return None
    event[0].created_user_id = handler.get_user(event[0].created_user_id).user_name

    users = []
    for subscriber_id in event[0].subscribers:
        users.append(handler.get_user(subscriber_id).user_name)
    event[0].subscribers = users
    return event[0]


@router.post("/add_subscriber/", dependencies=[Depends(rate_limit)])
def add_subscriber_to_event(
        event_id: str,
        user_id: str,
        handler: CombinedHandler = Depends(get_handler)
):
    handler.add_subscriber_to_event(event_id, user_id)
    return {"message": "Subscriber added successfully"}


@router.delete("/remove_subscriber/", dependencies=[Depends(rate_limit)])
def remove_subscriber_from_event(
        event_id: str,
        user_id: str,
        handler: CombinedHandler = Depends(get_handler)
):
    handler.remove_subscriber_from_event(event_id, user_id)
    return {"message": "Subscriber removed successfully"}


def check_for_upcoming_events(handler: CombinedHandler):
    """
    Check for events starting in the next 30 minutes and send reminders.
    """
    now = datetime.now(timezone.utc)
    twenty_nine_minutes_from_now = now + timedelta(minutes=29, hours=3)
    thirty_minutes_from_now = now + timedelta(minutes=30, hours=3)

    # Fetch all events starting between 29 and 30 minutes from now.
    upcoming_events = handler.events_handler.get_events(sort_by_attribute='event_start_time',
                                                        location_filter=None)
    for event in upcoming_events:
        if twenty_nine_minutes_from_now <= event.event_start_time <= thirty_minutes_from_now:
            handler.send_message(event.event_id, "It will start in 30 minutes.")


def reminder_background_task(handler: CombinedHandler):
    """
    Background task to run every minute and check for events starting in the next 30 minutes.
    """
    while True:
        check_for_upcoming_events(handler)
        time.sleep(60)  # Check every minute


@app.on_event("startup")
async def on_startup():
    handler = get_handler()
    thread = threading.Thread(target=reminder_background_task, args=(handler,))
    thread.daemon = True
    thread.start()


@app.on_event("shutdown")
def shutdown():
    handler = get_handler()
    handler.close()


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
