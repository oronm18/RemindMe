import threading
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, APIRouter, Depends

from common.server_handler import CombinedHandler

app = FastAPI()
router = APIRouter()


def get_handler():
    return CombinedHandler()


@router.post("/add_user/")
def add_user(
        username: str,
        mail: str,
        password: str,
        handler: CombinedHandler = Depends(get_handler)):
    return {"user_id": handler.add_user(username, mail, password)}


@router.get("/get_user/{user_id}/")
def get_user(user_id: str, handler: CombinedHandler = Depends(get_handler)):
    return handler.get_user(user_id)


@router.delete("/remove_user/{user_id}/")
def remove_user(user_id: str, handler: CombinedHandler = Depends(get_handler)):
    handler.remove_user(user_id)
    return {"message": "User removed successfully"}


@router.post("/schedule_event/")
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


@router.get("/get_event/{event_id}/")
def get_event(event_id: str, handler: CombinedHandler = Depends(get_handler)):
    return handler.get_event(event_id)


@router.delete("/remove_event/{event_id}/")
def remove_event(event_id: str, handler: CombinedHandler = Depends(get_handler)):
    handler.remove_event(event_id)
    return {"message": "Event removed successfully"}


@router.put("/modify_event/{event_id}/")
def modify_event(
        event_id: str,
        name: str = None,
        description: str = None,
        location: str = None,
        start: datetime = None,
        end: datetime = None,
        handler: CombinedHandler = Depends(get_handler)
):
    changes = {}
    if name: changes["event_name"] = name
    if description: changes["event_description"] = description
    if location: changes["location"] = location
    if start: changes["event_start_time"] = start
    if end: changes["event_end_time"] = end
    handler.modify_event(event_id, **changes)
    return {"message": "Event modified successfully"}


@router.get("/events")
def get_events_by_attribute(
        sort_by_attribute: str = None,  # Event
        reverse: bool = False,
        location: Optional[str] = None,
        handler: CombinedHandler = Depends(get_handler)
):
    return handler.get_events_by_attribute(sort_by_attribute, reverse, location_filter=location)


@router.post("/add_subscriber/")
def add_subscriber_to_event(
        event_id: str,
        user_id: str,
        handler: CombinedHandler = Depends(get_handler)
):
    handler.add_subscriber_to_event(event_id, user_id)
    return {"message": "Subscriber added successfully"}


@router.delete("/remove_subscriber/")
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
            handler.send_reminder(event.event_id)


def reminder_background_task(handler: CombinedHandler):
    """
    Background task to run every minute and check for events starting in the next 30 minutes.
    """
    import time
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
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
