# database.py
# by Preston Hager

import boto3
from botocore.exceptions import ClientError

import datetime

from uuid import uuid4
from secrets import token_urlsafe

dynamodb = boto3.resource('dynamodb')

class Database:
    def __init__(self, name, password_manager=None):
        self.table = dynamodb.Table(name)
        self.password_manager = password_manager

    def get_scoreboard(self, scoreboard_id):
        query = self.table.get_item(Key={'scoreboard_id': scoreboard_id})
        if "Item" not in query:
            return self._new_scoreboard(scoreboard_id)
        return query["Item"]

    def get_user(self, username):
        query = self.table.get_item(Key={'username': username})
        if "Item" not in query:
            return None
        return query["Item"]

    def get_access_key(self, access_key):
        query = self.table.get_item(Key={"key": str(access_key)})
        if "Item" not in query:
            return None
        return query["Item"]

    def new_listing(self, scoreboard_id, **kwargs):
        new_listing = {
            "listing_id": str(uuid4()),
            "name": "Unnamed",
            "total": 0
        }
        if "total" in kwargs:
            new_listing["total"] = kwargs["total"]
        if "name" in kwargs:
            new_listing["name"] = kwargs["name"]
        scoreboard = self.get_scoreboard(scoreboard_id)
        scoreboard["scores"][new_listing['listing_id']] = new_listing
        query = self._update_item('scoreboard_id', scoreboard_id, "set scores = :s", {":s": scoreboard["scores"]})
        return new_listing

    def new_user(self, username, password):
        new_user = {
            "username": username,
            "passhash": self.password_manager.hash_password(password)
        }
        self.table.put_item(Item=new_user)
        return new_user

    def new_access_key(self, username):
        new_key_item = {
            "key": token_urlsafe(32),
            "refresh_key": token_urlsafe(64),
            "expires":  (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat(),
            "username": username
        }
        self.table.put_item(Item=new_key_item)
        return new_key_item

    def update_listing(self, scoreboard_id, **kwargs):
        if "listing" in kwargs:
            scoreboard = self.get_scoreboard(scoreboard_id)
            if kwargs["listing"]["listing_id"] in scoreboard["scores"]:
                scoreboard["scores"][kwargs["listing"]["listing_id"]].update(kwargs["listing"])
                query = self._update_item('scoreboard_id', scoreboard_id, "set scores = :s", {":s": scoreboard["scores"]})
                return scoreboard["scores"][kwargs["listing"]["listing_id"]]
            else:
                raise ValueError(f"Listing with id `{kwargs['listing']['listing_id']}` does not exist.")

    def update_scoreboard(self, scoreboard_id, **kwargs):
        if "title" in kwargs:
            query = self._update_item('scoreboard_id', scoreboard_id, "set title = :t", {":t": kwargs["title"]})
        elif "scores" in kwargs:
            query = self._update_item('scoreboard_id', scoreboard_id, "set scores = :s", {":s": kwargs["scores"]})

    def delete_listing(self, scoreboard_id, listing_id):
        scoreboard = self.get_scoreboard(scoreboard_id)
        if listing_id in scoreboard["scores"]:
            del scoreboard["scores"][listing_id]
            query = self._update_item('scoreboard_id', scoreboard_id, "set scores = :s", {":s": scoreboard["scores"]})
            return True
        else:
            raise ValueError(f"Listing with id `{listing_id}` does not exist.")

    def _new_scoreboard(self, scoreboard_id):
        new_scoreboard = {
            "scoreboard_id": scoreboard_id,
            "title": "Untitled",
            "scores": {}
        }
        self.table.put_item(Item=new_scoreboard)
        return new_scoreboard

    def _update_item(self, key, key_id, expression, values):
        query = self.table.update_item(Key={key: key_id}, UpdateExpression=expression, ExpressionAttributeValues=values, ReturnValues="ALL_NEW")
        return query

__all__ = ["Database"]
