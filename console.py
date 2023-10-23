"""
CLI Application for interacting with a remote API.
Author: Oron Moshe
Date: 23/10/2023
"""

"""
THIS FILE IS ONLY FOR TEST THE API ROUTES VIA CONSOLE.
"""

# ----- Imports ----- #

import requests
import datetime

# ----- Constants ----- #

BASE_URL = "http://127.0.0.1:8000"


class CLIApp:
    """ Command-Line Application for User and Event Management """

    def __init__(self):
        """ Initialize the CLIApp """
        self.current_user_id = None

    @staticmethod
    def display_header(title):
        """ Display a header for each menu/option. """
        print("\n" + "=" * 30)
        print(title.center(30))
        print("=" * 30)

    def run(self):
        """
        Display the main menu and handle user choices.
        """
        self.display_header("Main Menu")
        while True:
            print("\nOptions:")
            options = ['Exit', 'Login', 'Register', 'Get User Info', 'Schedule an Event',
                       'Get Event Info', 'Retrieve Events by Location', 'Sort and Retrieve Events']
            for i, option in enumerate(options):
                print(f"{i}. {option}")

            choice = input("\nEnter your choice: ")

            actions = {
                "1": self.login,
                "2": self.register,
                "3": self.get_user_info,
                "4": self.schedule_event,
                "5": self.get_event_info,
                "6": self.retrieve_events_by_location,
                "7": self.sort_and_retrieve_events,
                "0": lambda: exit()
            }

            action = actions.get(choice, None)
            if action:
                action()
            else:
                print("\nInvalid choice. Please try again.")

    def login(self):
        """
        Prompt the user to input login credentials and attempt to login.
        Update the `current_user_id` if login is successful.
        """
        self.display_header("Login")
        username = input("Enter username: ")
        password = input("Enter password: ")

        try:
            response = requests.post(f"{BASE_URL}/login/?username={username}&password={password}")
            response.raise_for_status()

            print("\nLogin successful!")
            self.current_user_id = response.json()["user_id"]
            print("Logged in with User ID:", self.current_user_id)
        except requests.HTTPError:
            print("\nError:", response.json()["detail"])

    def register(self):
        """
        Prompt the user to input registration details and attempt to register a new account.
        Update the `current_user_id` if registration is successful.
        """
        username = input("Enter username: ")
        mail = input("Enter email: ")
        password = input("Enter password: ")

        response = requests.post(f"{BASE_URL}/register/?username={username}&mail={mail}&password={password}")

        if response.status_code == 200:
            print("Registration successful!")
            self.current_user_id = response.json()["user_id"]
            print("Registered with User ID:", self.current_user_id)
        else:
            print("Error:", response.json()["detail"])

    def get_user_info(self):
        """
        Fetch and display the current user's information from the server.
        """
        if not self.current_user_id:
            print("Please login or register first.")
            return

        response = requests.get(f"{BASE_URL}/get_user/{self.current_user_id}/")
        if response.status_code == 200:
            user_data = response.json()
            print("User Data:", user_data)
        else:
            print("Error:", response.json()["detail"])

    def schedule_event(self):
        """
        Prompt the user to input event details and attempt to schedule a new event.
        """
        if not self.current_user_id:
            print("Please login or register first.")
            return

        name = input("Enter event name: ")
        description = input("Enter event description: ")
        location = input("Enter event location: ")
        start = get_correct_datetime_input("Enter event start date-time (YYYY-MM-DD HH:MM:SS): ")
        end = get_correct_datetime_input("Enter event end date-time (YYYY-MM-DD HH:MM:SS): ")

        start_dt = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

        response = requests.post(f"{BASE_URL}/schedule_event/?user_id={self.current_user_id}"
                                 f"&name={name}&description={description}&location={location}"
                                 f"&start={start_dt}&end={end_dt}")

        if response.status_code == 200:
            print("Event scheduled successfully!")
            print("Event ID:", response.json()["event_id"])
        else:
            print("Error:", response.json()["detail"])

    def get_event_info(self):
        """
        Prompt the user to input an event name and fetch the corresponding event details.
        """
        if not self.current_user_id:
            print("Please login or register first.")
            return

        event_name = input("Enter event name: ")

        response = requests.get(f"{BASE_URL}/get_event/{event_name}/")
        if response.status_code == 200:
            event_data = response.json()
            print("Event Data:", event_data)
        else:
            print("Error:", response.json()["detail"])

    def retrieve_events_by_location(self):
        """
        Prompt the user to input a location and retrieve a list of events for that location.
        """
        if not self.current_user_id:
            print("Please login or register first.")
            return

        location = input("Enter event location or venue: ")

        response = requests.get(f"{BASE_URL}/events", params={"location": location})
        if response.status_code == 200:
            events = response.json()
            print("\nEvents in", location, ":")
            for event in events:
                print(event)
        else:
            print("Error:", response.json()["detail"])

    def sort_and_retrieve_events(self):
        """
        Prompt the user to choose a sorting criteria and retrieve a sorted list of events based on that criteria.
        """
        if not self.current_user_id:
            print("Please login or register first.")
            return

        print("Choose sorting criteria:")
        print("1. Date")
        print("2. Popularity (number of participants)")
        print("3. Creation time")
        choice = input("Enter your choice: ")

        sort_by = None
        if choice == "1":
            sort_by = "event_start_time"
        elif choice == "2":
            sort_by = "subscribers"
        elif choice == "3":
            sort_by = "creation_time"
        else:
            print("Invalid choice. Returning to main menu.")
            return

        response = requests.get(f"{BASE_URL}/events", params={"sort_by_attribute": sort_by})
        if response.status_code == 200:
            events = response.json()
            print("\nEvents sorted by", sort_by, ":")
            for event in events:
                print(event)
        else:
            print("Error:", response.json()["detail"])


def get_correct_datetime_input(msg: str) -> str:
    """
    Repeatedly prompt the user for a date-time string until a valid format is provided.
    :param msg: Prompt message to display.
    :return: Valid date-time string in the format YYYY-MM-DD HH:MM:SS.
    """
    while True:
        start = input(msg)
        try:
            datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            return start
        except ValueError:
            print("Invalid format. Please enter date-time in the format YYYY-MM-DD HH:MM:SS.")


if __name__ == "__main__":
    app = CLIApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nExiting the application.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}. Exiting.")