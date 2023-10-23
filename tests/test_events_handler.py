import pytest
from core.event import Event, EventAlreadyExist, ModifyChangesAreInvalid, InvalidAttribute, \
    UserDoesNotASubscriber, UserAlreadySubscriber
from common.events_handler import EventsHandler
import tempfile
import os
from datetime import datetime

now = datetime.now()


@pytest.fixture
def temp_db_file():
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)


@pytest.fixture
def events_handler(temp_db_file):
    return EventsHandler(temp_db_file)


def test_add_event(events_handler):
    event = Event(event_id=None, created_user_id="user1", event_name="Event1", event_description="Description",
                  location="Holon", subscribers=[], event_start_time=now, event_end_time=now, creation_time=now)
    event_id = events_handler.add_event(event)
    assert event_id is not None

    # Test adding the same event again
    with pytest.raises(EventAlreadyExist):
        events_handler.add_event(event)


def test_remove_event(events_handler):
    event = Event(event_id=None, created_user_id="user1", event_name="Event1", event_description="Description",
                  location="Holon", subscribers=[], event_start_time=now, event_end_time=now, creation_time=now)
    event_id = events_handler.add_event(event)

    events_handler.remove_event(event_id)

    events = events_handler.get_events_by_ids([event_id])
    assert len(events) == 0


def test_modify_event(events_handler):
    event = Event(event_id=None, created_user_id="user1", event_name="Event1", event_description="Description",
                  location="Holon", subscribers=[], event_start_time=now, event_end_time=now, creation_time=now)
    event_id = events_handler.add_event(event)

    changes = {"event_name": "UpdatedEvent", "location": "UpdatedHolon"}
    events_handler.modify_event(event_id, **changes)

    updated_event = events_handler.get_event(event_id)
    assert updated_event.event_name == "UpdatedEvent"
    assert updated_event.location == "UpdatedHolon"

    with pytest.raises(ModifyChangesAreInvalid):
        events_handler.modify_event(event_id, invalid_attribute="Invalid")


def test_get_event(events_handler):
    event = Event(event_id=None, created_user_id="user1", event_name="Event1", event_description="Description",
                  location="Holon", subscribers=[], event_start_time=now, event_end_time=now, creation_time=now)
    event_id = events_handler.add_event(event)

    fetched_event = events_handler.get_event(event_id)
    assert fetched_event.event_name == "Event1"
    assert fetched_event.location == "Holon"


def test_add_remove_subscriber(events_handler):
    event = Event(event_id=None, created_user_id="user1", event_name="Event1", event_description="Description",
                  location="Holon", subscribers=[], event_start_time=now, event_end_time=now, creation_time=now)
    event_id = events_handler.add_event(event)

    events_handler.add_subscriber(event_id, "user2")
    updated_event = events_handler.get_event(event_id)
    assert "user2" in updated_event.subscribers

    with pytest.raises(UserAlreadySubscriber):
        events_handler.add_subscriber(event_id, "user2")

    events_handler.remove_subscriber(event_id, "user2")
    updated_event = events_handler.get_event(event_id)
    assert "user2" not in updated_event.subscribers

    with pytest.raises(UserDoesNotASubscriber):
        events_handler.remove_subscriber(event_id, "user2")


def test_get_events(events_handler):
    event1 = Event(event_id=None, created_user_id="user1", event_name="Event1", event_description="Description",
                   location="Tel Aviv", subscribers=[], event_start_time=now, event_end_time=now, creation_time=now)
    event2 = Event(event_id=None, created_user_id="user1", event_name="Event2", event_description="Description",
                   location="Haifa", subscribers=[], event_start_time=now, event_end_time=now, creation_time=now)
    events_handler.add_event(event1)
    events_handler.add_event(event2)

    events = events_handler.get_events()
    assert len(events) == 2

    events = events_handler.get_events(location="Tel Aviv")
    assert len(events) == 1
    assert events[0].location == "Tel Aviv"


if __name__ == "__main__":
    pytest.main()
