"""
Database handler file.
Author: Oron Moshe
Date: 22/10/2023
"""
# ----- Imports ----- #

import sqlite3
from pathlib import Path
from typing import Union

# ----- Constants ----- #

DATABASE_NAME = "data.db"


# ----- Classes ----- #

class DatabaseHandler:
    def __init__(self, database_file: Union[str, Path] = DATABASE_NAME):
        """
        Init the handler class.
        :param database_file: The database.
        """
        self._users_database_path: Path = Path(database_file)
        self.conn = sqlite3.connect(database_file)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()
