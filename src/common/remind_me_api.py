from datetime import datetime
from typing import Optional

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel

from common.server_handler import CombinedHandler
from core.event import Event

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


@router.post("/add_event/")
def add_event(
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
def modify_event(event_id: str, changes: dict, handler: CombinedHandler = Depends(get_handler)):
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


@app.on_event("shutdown")
def shutdown():
    handler = get_handler()
    handler.close()


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
