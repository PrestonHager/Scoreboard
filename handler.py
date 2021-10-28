# handler.py
# by Preston Hager

import database
import json

from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader(searchpath="templates"),
    autoescape=select_autoescape()
)

class Handler:
    def __init__(self):
        self.scoreboard_table = database.Database('scoreboard-scoreboards')
        self.users_table = database.Database('scoreboard-users')

    def create_response(self, content, code, content_type="text/html"):
        return {
            "statusCode": code,
            "body": content,
            "headers": {
                "Content-Type": content_type
            }
        }

    def index(self, event, context):
        scoreboard = self.scoreboard_table.get_scoreboard("d288202a-3fc1-475f-be96-5567a605b287")
        template = env.get_template("index.html")
        content = template.render(scores=scoreboard['scores'])
        return self.create_response(content, 200)

    def auth(self, event, context):
        event_body = json.loads(event['body'])
        username = event_body['username']
        return self.create_response(authorization, 200, "application/json")

_inst = Handler()
index = _inst.index
