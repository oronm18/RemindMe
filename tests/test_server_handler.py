import pytest
from datetime import datetime
from common.server_handler import CombinedHandler
import tempfile
import os


@pytest.fixture
def temp_db_file():
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)


@pytest.fixture
def handler(temp_db_file):
    return CombinedHandler(temp_db_file, temp_db_file)


def test_add_get_user(handler):
    user_id = handler.add_user("Oron", "oron@gmail.com", "111")
    user = handler.get_user(user_id)
    assert user.user_name == "Oron"
    assert user.user_mail == "oron@gmail.com"


def test_remove_user(handler):
    user_id = handler.add_user("Oron", "oron@gmail.com", "111")
    handler.remove_user(user_id)
    with pytest.raises(Exception):
        handler.get_user(user_id)


def test_add_get_event(handler):
    user_id = handler.add_user("Oron", "oron@gmail.com", "111")
    event_id = handler.add_event(user_id, "event", "Hello", "Holon", [], datetime.now())
    event = handler.get_event(event_id)
    assert event.event_name == "event"
    assert event.location == "Holon"


def test_remove_event(handler):
    user_id = handler.add_user("Oron", "oron@gmail.com", "111")
    event_id = handler.add_event(user_id, "event", "Hello", "Holon", [], datetime.now())
    handler.remove_event(event_id)
    with pytest.raises(Exception):
        handler.get_event(event_id)


def test_modify_event(handler):
    user_id = handler.add_user("Oron", "oron@gmail.com", "111")
    event_id = handler.add_event(user_id, "event", "Hello", "Holon", [], datetime.now())
    handler.modify_event(event_id, location="Tel Aviv")
    event = handler.get_event(event_id)
    assert event.location == "Tel Aviv"


def test_add_remove_subscriber_to_event(handler):
    user_id = handler.add_user("Oron", "oron@gmail.com", "111")
    user2_id = handler.add_user("user2", "user2@gmail.com", "222")
    event_id = handler.add_event(user_id, "event", "Hello", "Holon", [], datetime.now())
    handler.add_subscriber_to_event(event_id, user2_id)
    event = handler.get_event(event_id)
    assert user2_id in event.subscribers
    handler.remove_subscriber_from_event(event_id, user2_id)
    event = handler.get_event(event_id)
    assert user2_id not in event.subscribers


if __name__ == "__main__":
    pytest.main()
