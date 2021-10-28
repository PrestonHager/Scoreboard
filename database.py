# database.py
# by Preston Hager

import boto3

from uuid import uuid4

dynamodb = boto3.resource('dynamodb')

class Database:
    def __init__(self, name):
        self.table = dynamodb.Table(name)

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

    def new_listing(self, scoreboard_id, new_listing, data={}):
        new_listing = {
            "listing_id": str(uuid4()),
            "total": 0
        }
        scoreboard = self.get_scoreboard(scoreboard_id)
        scoreboard["scores"][new_listing['listing_id']] = new_listing
        query = self._update_item('scoreboard_id', scoreboard_id, "set scores = :s", {":s": scoreboard["scores"]})
        return new_listing

    def new_user(self, username, password):
        new_user = {
            "username": username,
            "passhash": ""
        }
        self.table.put_item(Item=new_user)
        return new_user

    def update_listing(self, scoreboard_id, listing_id, **kwargs):
        if "listing" in kwargs:
            query = self._update_item('scoreboard_id', scoreboard_id, "set scores = :s", {":s": kwargs["listing"]["scores"]})
        elif "scores" in kwargs:
            query = self._update_item('scoreboard_id', scoreboard_id, "set scores = :s", {":s": kwargs["scores"]})

    def _new_scoreboard(self, scoreboard_id):
        new_scoreboard = {
            "scoreboard_id": scoreboard_id,
            "scores": {}
        }
        self.table.put_item(Item=new_scoreboard)
        return new_scoreboard

    def _update_item(self, key, key_id, expression, values):
        query = self.table.update_item(Key={key: key_id}, UpdateExpression=expression, ExpressionAttributeValues=values, ReturnValues="ALL_NEW")
        return query
