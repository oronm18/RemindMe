import pytest
from core.user import User, UserAlreadyExist, UserDoesNotExist, EventAlreadyInUser, EventDoesNotInUser
from common.users_handler import UsersHandler
import tempfile
import os


@pytest.fixture
def temp_db_file():
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)


@pytest.fixture
def users_handler(temp_db_file):
    return UsersHandler(temp_db_file)


def test_add_user(users_handler):
    user = User(user_id=None, user_name="Oron", user_mail="Oron@gmail.com", hashed_password="")
    user_id = users_handler.add_user(user, "111")
    assert user_id is not None

    # Test adding the same user again
    with pytest.raises(UserAlreadyExist):
        users_handler.add_user(user, "111")


def test_get_user(users_handler):
    user = User(user_id=None, user_name="Oron", user_mail="Oron@gmail.com", hashed_password="")
    user_id = users_handler.add_user(user, "111")

    fetched_user = users_handler.get_user(user_id)
    assert fetched_user.user_name == "Oron"
    assert fetched_user.user_mail == "Oron@gmail.com"

    with pytest.raises(UserDoesNotExist):
        users_handler.get_user("invalid_id")


def test_remove_user(users_handler):
    user = User(user_id=None, user_name="Oron", user_mail="Oron@gmail.com", hashed_password="")
    user_id = users_handler.add_user(user, "111")

    users_handler.remove_user(user_id)

    with pytest.raises(UserDoesNotExist):
        users_handler.get_user(user_id)


def test_add_event_to_user(users_handler):
    user = User(user_id=None, user_name="Oron", user_mail="Oron@gmail.com", hashed_password="")
    user_id = users_handler.add_user(user, "111")

    users_handler.add_event_tp_user(user_id, "event1")

    with pytest.raises(EventAlreadyInUser):
        users_handler.add_event_tp_user(user_id, "event1")


def test_remove_event_from_user(users_handler):
    user = User(user_id=None, user_name="Oron", user_mail="Oron@gmail.com", hashed_password="")
    user_id = users_handler.add_user(user, "111")

    users_handler.add_event_tp_user(user_id, "event1")
    users_handler.remove_event_from_user(user_id, "event1")

    with pytest.raises(EventDoesNotInUser):
        users_handler.remove_event_from_user(user_id, "event1")


def test_get_user_id_by_name(users_handler):
    user = User(user_id=None, user_name="Oron", user_mail="Oron@gmail.com", hashed_password="")
    user_id = users_handler.add_user(user, "111")

    fetched_user_id = users_handler.get_user_id_by_name("Oron")
    assert fetched_user_id == user_id

    with pytest.raises(UserDoesNotExist):
        users_handler.get_user_id_by_name("InvalidName")


if __name__ == "__main__":
    pytest.main()
