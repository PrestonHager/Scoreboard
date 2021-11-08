# handler.py
# by Preston Hager

import sys
sys.path.append("./lib")

import json

from jinja2 import Environment, FileSystemLoader, select_autoescape

from database import *
from password_manager import *

env = Environment(
    loader=FileSystemLoader(searchpath="templates"),
    autoescape=select_autoescape()
)

with open("errors.json", 'r') as f_in:
    ERRORS = json.load(f_in)

MIMETYPES = {
    "css": "text/css",
    "js": "application/javascript",
    "html": "text/html"
}

class Handler:
    def __init__(self):
        self.password_manager = PasswordManager()
        self.scoreboard_table = Database('scoreboard-scoreboards')
        self.users_table = Database('scoreboard-users', self.password_manager)
        self.authorizations_table = Database('scoreboard-authorizations')
        self.authorization_manager = AuthorizationManager(self.authorizations_table)
        self.DEFAULT_SCOREBOARD = "d288202a-3fc1-475f-be96-5567a605b287"

    def index(self, event, context):
        scoreboard = self.scoreboard_table.get_scoreboard(self.DEFAULT_SCOREBOARD)
        template = env.get_template("index.html")
        content = template.render(scores=scoreboard['scores'], name=scoreboard['name'])
        return self.create_response(content, 200)

    def add_listing(self, event, context):
        try:
            event_body = json.loads(event['body'])
            access_key = event_body['access_key']
        except KeyError:
            return self.create_response(self._error(1), 400, "application/json")
        if not self.authorization_manager.check(access_key):
            return self.create_response(self._error(4), 401, "application/json")
        total = event_body["total"] if "total" in event_body else 0
        new_listing = self.scoreboard_table.new_listing(self.DEFAULT_SCOREBOARD, total=total)
        return new_listing

    def edit_listing(self, event, context):
        pass

    def static(self, event, context):
        filename = event["pathParameters"]["filename"]
        # NOTE: this isn't very secure, but it works for our purposes
        # in reality you should check for the filename existing
        # so as to prevent back tracing.
        with open("static/" + filename, 'r') as f_in:
            content = f_in.read()
        file_ending = filename.split('.')[-1]
        if file_ending in MIMETYPES:
            return self.create_response(content, 200, MIMETYPES[file_ending])
        else:
            return self.create_response(content, 200)

    def auth(self, event, context):
        try:
            event_body = json.loads(event['body'])
            username = event_body['username']
            password = event_body['password']
        except KeyError:
            return self.create_response(self._error(1), 400, "application/json")
        user = self.users_table.get_user(username)
        if user == None:
            return self.create_response(self._error(2), 400, "application/json")
        if not self.password_manager.compare(password, user['passhash']):
            return self.create_response(self._error(3), 401, "application/json")
        authorization = self.authorization_manager.generate_authorization(username)
        return self.create_response(authorization, 200, "application/json")

    def create_response(self, content, code, content_type="text/html"):
        return {
            "statusCode": code,
            "body": content,
            "headers": {
                "Content-Type": content_type
            }
        }

    def _error(self, code):
        error = {
            "error": ERRORS[str(code)]["message"],
            "code": code
        }
        return error

_inst = Handler()
index = _inst.index
auth = _inst.auth
add_listing = _inst.add_listing
edit_listing = _inst.edit_listing
static = _inst.static
