=================
RemindMe Project
=================

:Author: Oron Moshe
:Date: 22/10/2023

Overview
--------
RemindMe is a backend tool that simplifies event and account management for users, ensuring a smooth events.

Features
--------
- User Account Management: Register, modify, or delete accounts.
- Event Scheduling: Plan, adjust, or remove events as per requirements.
- Subscriber Management: Effortlessly add or delete subscribers for specific events.
- Event Retrieval: Acquire event details based on unique attributes.

Components
----------
1. **Core Components**: 
    - Houses essential definitions for users and events.
    - Handles related exceptions.

2. **Database Handler**: 
    - Orchestrates SQLite database operations.
    - Manages user and event data.

3. **Server Handler**: 
    - Acts as an intermediary for both user and event database operations.

4. **API Server**: 
    - Implements a FastAPI server.
    - Offers endpoints to facilitate user and event management.

Dependencies
------------
- `FastAPI`
- `uvicorn`
- `pydantic`
- `bcrypt`

Getting Started
---------------
1. Ensure all dependencies are installed on your system.
2. Clone the RemindMe repository.
3. Activate the server:

   .. code-block:: bash

      cd src
      python remind_me_api.py

4. Navigate to `http://127.0.0.1:8000` on your browser to access the API documentation and interact with available endpoints.

API Endpoints
-------------
1. **User Management**:
   - POST `/add_user/`: Register new users.
   - GET `/get_user/{user_id}/`: Retrieve user details via ID.
   - DELETE `/remove_user/{user_id}/`: Remove a user based on ID.

2. **Event Management**:
   - POST `/schedule_event/`: Plan a new event.
   - GET `/get_event/{event_id}/`: Obtain event particulars using ID.
   - DELETE `/remove_event/{event_id}/`: Erase an event by its ID.
   - PUT `/modify_event/{event_id}/`: Update event details.
   - GET `/events`: Extract events based on specific attributes.

3. **Subscriber Management**:
   - POST `/add_subscriber/`: Enlist a subscriber for an event.
   - DELETE `/remove_subscriber/`: Expel a subscriber from an event.

Timely Alerts
-------------
The server performs checks every minute to determine if there are events scheduled for the upcoming 30 minutes, ensuring users are always reminded in a timely manner.
