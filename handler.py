# handler.py
# by Preston Hager

# Add the "./lib" directory to the import path for custom imports and dependencies
import sys
sys.path.append("./lib")

# All the imports needed for the handler
import json

from jinja2 import Environment, FileSystemLoader, select_autoescape

from database import *
from password_manager import *

# Setup the Jinja environment which holds a file system loader for templates
env = Environment(
    loader=FileSystemLoader(searchpath="templates"),
    autoescape=select_autoescape()
)

# Set the errors through the json data file
with open("errors.json", 'r') as f_in:
    ERRORS = json.load(f_in)

# Set the mimetypes for file extensions in the static directory
MIMETYPES = {
    "css": "text/css",
    "js": "application/javascript",
    "html": "text/html"
}

# Main handler class, holds all functions
class Handler:
    def __init__(self):
        """
        Handler.__init__

        Setup all databases and managers.
        """
        self.password_manager = PasswordManager()
        self.scoreboard_table = Database('scoreboard-scoreboards')
        self.users_table = Database('scoreboard-users', self.password_manager)
        self.authorizations_table = Database('scoreboard-authorizations')
        self.authorization_manager = AuthorizationManager(self.authorizations_table)
        # The default scoreboard
        # TODO: add a list of scoreboards and allow users to create new scoreboards
        self.DEFAULT_SCOREBOARD = "d288202a-3fc1-475f-be96-5567a605b287"

    def index(self, event, context):
        """
        Handler.index

        Index page of the handler, takes in an AWS Lambda event.
        """
        scoreboard = self.scoreboard_table.get_scoreboard(self.DEFAULT_SCOREBOARD)
        template = env.get_template("index.html")
        content = template.render(scores=scoreboard['scores'], name=scoreboard['name'])
        return self.create_response(content, 200)

    def edit(self, event, context):
        """
        Handler.edit

        Edit page of the handler, takes in an AWS Lambda event.
        Returns either an edit page or a login page based on authorization.
        """
        # Test for an authorization token in the cookies
        # If it's found, show the edit page for the selected scoreboard
        scoreboard = self.scoreboard_table.get_scoreboard(self.DEFAULT_SCOREBOARD)
        template = env.get_template("edit.html")
        content = template.render(scores=scoreaboard['scores'], name=scoreboard['name'])
        return self.create_response(content, 200)
        # If it's not found, show the login page
        template = env.get_template("login.html")
        content = template.render()
        return self.create_response(content, 200)

    def add_listing(self, event, context):
        """
        Handler.add_listing

        Add a listing to the selected scoreboard through a POST.
        Takes an AWS Lambda event with a valid authorization token and a body with data.
        """
        # Load in the event body
        try:
            event_body = json.loads(event['body'])
            access_key = event_body['access_key']
        except KeyError:
            return self.create_response(self._error(1), 400, "application/json")
        # Check the authorization token against the manager
        if not self.authorization_manager.check(access_key):
            return self.create_response(self._error(4), 401, "application/json")
        # Create a new listing based on information given and return it
        total = event_body["total"] if "total" in event_body else 0
        name = event_body["name"] if "name" in event_body else "Unnamed"
        new_listing = self.scoreboard_table.new_listing(self.DEFAULT_SCOREBOARD, total=total, name=name)
        return new_listing

    def edit_listing(self, event, context):
        pass

    def edit_scoreboard(self, event, context):
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

    def create_redirect(self, url):
        return {
            "statusCode": 302,
            "headers": {
                "Location": url
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
