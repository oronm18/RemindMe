RemindMe Project
================

:Author: Oron Moshe
:Date: 22/10/2023

Description
-----------

RemindMe is a backend project that helps users manage their events.
It allows users to:

- Register and manage user accounts.
- Schedule, modify, and delete events.
- Add or remove subscribers to events.
- Fetch events based on specific attributes.

Components
----------

1. **Core Components**: Contains the base definitions of a user and event, as well as relevant exceptions.
2. **Database Handler**: Manages SQLite database operations for users and events.
3. **Server Handler**: Provides an interface to interact with both user and event database handlers.
4. **API Server**: A FastAPI server that exposes endpoints for managing users and events.

Dependencies
------------

- `FastAPI`
- `uvicorn`
- `pydantic`

Quickstart
----------

1. Ensure you have all dependencies installed.
2. Clone the repository.
3. Run the server:

   .. code-block:: bash

      $ uvicorn main:app --reload

4. Visit `http://127.0.0.1:8000` in your browser to access the API documentation and test endpoints.

API Endpoints
-------------

1. **User Management**:
   - POST `/add_user/`: Register a new user.
   - GET `/get_user/{user_id}/`: Fetch user details by ID.
   - DELETE `/remove_user/{user_id}/`: Delete a user by ID.

2. **Event Management**:
   - POST `/schedule_event/`: Schedule a new event.
   - GET `/get_event/{event_id}/`: Fetch event details by ID.
   - DELETE `/remove_event/{event_id}/`: Delete an event by ID.
   - PUT `/modify_event/{event_id}/`: Modify an existing event.
   - GET `/events`: Fetch events based on specific attributes.

3. **Subscriber Management**:
   - POST `/add_subscriber/`: Add a subscriber to an event.
   - DELETE `/remove_subscriber/`: Remove a subscriber from an event.
