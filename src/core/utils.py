"""
Utils file for the project
Author: Oron Moshe
Date: 22/10/2023
"""
# ----- Imports ----- #
import dataclasses
import datetime
import json
import uuid
import bcrypt


# ----- Functions ----- #

def generate_unique_id() -> str:
    """
    Generate a unique id for an item.
    :return: A new unique id.
    """
    return str(uuid.uuid4())


def compare_hashes(hash1: str, hash2: str) -> bool:
    """
    Compare 2 given hashes.
    :param hash1: First given hash.
    :param hash2: Second given hash.
    :return: Does the hashes equals?
    """
    return bcrypt.checkpw(hash1.encode('utf-8'), hash2.encode('utf-8'))


def hash_password(password: str) -> str:
    """
    Hash a password.
    :param password: Given password.
    :return: The hashed input.
    """
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)
