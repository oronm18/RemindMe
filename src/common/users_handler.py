"""
User handler file.
Author: Oron Moshe
Date: 22/10/2023
"""
# ----- Imports ----- #

import json
from pathlib import Path
from typing import Union

from core.database_handler import DatabaseHandler
from core.user import User, UserAlreadyExist, UserDoesNotExist, EventAlreadyInUser, EventDoesNotInUser
from core.utils import generate_unique_id, hash_password


# ----- Classes ----- #

class UsersHandler(DatabaseHandler):
    def __init__(self, users_database_file: Union[str, Path]):
        """
        Init the user handler class.
        :param users_database_file: The user database.
        """
        super().__init__(users_database_file)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users
            (user_id TEXT PRIMARY KEY, 
            user_name TEXT UNIQUE, 
            user_mail TEXT,
            hashed_password TEXT,
            hosts_events TEXT DEFAULT '[]')
        ''')

    def add_user(self, user: User, password: str) -> str:
        """
        Add user to data base.
        :param user: Given user to add.
        :param password: Password.
        :return: User id.
        """
        self.cursor.execute("SELECT user_id FROM users WHERE user_name=?", (user.user_name,))
        if self.cursor.fetchone():
            raise UserAlreadyExist("A user with this name already exists.")

        user.user_id = generate_unique_id()
        user.hashed_password = hash_password(password)

        self.cursor.execute("INSERT INTO users (user_id, user_name, user_mail, hashed_password) VALUES (?, ?, ?, ?)",
                            (user.user_id, user.user_name, user.user_mail, user.hashed_password))
        self.conn.commit()
        return user.user_id

    def get_user(self, user_id):
        """
        Get user by id from database.
        :param user_id: Given user id.
        :return: User.
        """
        self.cursor.execute("SELECT user_id, user_name, user_mail, hashed_password FROM users WHERE user_id=?",
                            (user_id,))
        result = self.cursor.fetchone()
        if not result:
            raise UserDoesNotExist()
        return User(user_id=result[0], user_name=result[1], user_mail=result[2], hashed_password=result[3])

    def remove_user(self, user_id: str):
        """
        Remove user from data base.
        :param user_id: Given user id to remove
        """
        self.get_user(user_id)
        self.cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        self.conn.commit()

    def add_event_tp_user(self, user_id: str, event_id: str):
        """
        Add event id to user.
        :param user_id: Given user to add the event.
        :param event_id: Given event id to add.
        """
        # Fetch the current list of event IDs for the user
        self.cursor.execute("SELECT hosts_events FROM users WHERE user_id=?", (user_id,))
        result = self.cursor.fetchone()
        if not result:
            raise UserDoesNotExist()

        # Deserialize the events list and check if the event ID already exists
        events_list = json.loads(result[0])
        if event_id in events_list:
            raise EventAlreadyInUser()

        # Append the new event ID and serialize the updated list
        events_list.append(event_id)
        serialized_events = json.dumps(events_list)

        # Update the user's events list in the database
        self.cursor.execute("UPDATE users SET hosts_events=? WHERE user_id=?", (serialized_events, user_id))
        self.conn.commit()

    def remove_event_from_user(self, user_id: str, event_id: str):
        """
        Remove event id from user.
        :param user_id: Given user to remove the event.
        :param event_id: Given event id to remove.
        """
        # Fetch the current list of event IDs for the user
        self.cursor.execute("SELECT hosts_events FROM users WHERE user_id=?", (user_id,))
        result = self.cursor.fetchone()
        if not result:
            raise UserDoesNotExist()

        # Deserialize the events list and check if the event ID exists
        events_list = json.loads(result[0])
        if event_id not in events_list:
            raise EventDoesNotInUser()

        # Remove the event ID and serialize the updated list
        events_list.remove(event_id)
        serialized_events = json.dumps(events_list)

        # Update the user's events list in the database
        self.cursor.execute("UPDATE users SET hosts_events=? WHERE user_id=?", (serialized_events, user_id))
        self.conn.commit()

    def get_user_id_by_name(self, user_name: str) -> str:
        """
        Get user ID by its name from the database.
        :param user_name: Name of the user.
        :return: User ID.
        """
        self.cursor.execute("SELECT user_id FROM users WHERE user_name=?", (user_name,))
        result = self.cursor.fetchone()
        if not result:
            raise UserDoesNotExist(user_name)
        return result[0]

    @staticmethod
    def send_mail(user: User, message: str):
        print(f"Sending mail with {message} to {user.user_mail}")
