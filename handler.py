# handler.py
# by Preston Hager

# Add the "./lib" directory to the import path for custom imports and dependencies
import sys
sys.path.append("./lib")

# All the imports needed for the handler
import json
from urllib.parse import parse_qs
from http.cookies import SimpleCookie

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
        content = template.render(scores=scoreboard['scores'], title=scoreboard['title'])
        return self.create_response(content, 200)

    def edit(self, event, context):
        """
        Handler.edit

        Edit page of the handler, takes in an AWS Lambda event.
        Returns either an edit page or a login page based on authorization.
        """
        # Test for an authorization token in the cookies
        cookie = self._parse_cookie(event['headers'])
        if cookie and self._check_auth(cookie):
            # If it's found, show the edit page for the selected scoreboard
            scoreboard = self.scoreboard_table.get_scoreboard(self.DEFAULT_SCOREBOARD)
            template = env.get_template("edit.html")
            content = template.render(scores=scoreboard['scores'], title=scoreboard['title'])
            return self.create_response(content, 200)
        else:
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
        # Check for authorization then proceed
        cookie = self._parse_cookie(event['headers'])
        if not cookie or not self._check_auth(cookie):
            return self.create_response(self._error(4), 401, "application/json")
        # Load in the event body
        try:
            event_body = json.loads(event['body'])
        except KeyError:
            return self.create_response(self._error(1), 400, "application/json")
        # Create a new listing based on information given and return it
        total = event_body["total"] if "total" in event_body else 0
        name = event_body["name"] if "name" in event_body else "Unnamed"
        new_listing = self.scoreboard_table.new_listing(self.DEFAULT_SCOREBOARD, total=total, name=name)
        return self.create_response(json.dumps(new_listing), 200, "application/json")

    def edit_listing(self, event, context):
        """
        Handler.edit_listing

        Edit a listing to the selected scoreboard through a POST.
        Takes an AWS Lambda event with a valid authorization token and a body with data.
        """
        # Check for authorization then proceed
        cookie = self._parse_cookie(event['headers'])
        if not cookie or not self._check_auth(cookie):
            return self.create_response(self._error(4), 401, "application/json")
        # Load in the event body
        try:
            event_body = json.loads(event['body'])
            listing_id = event_body["listing_id"]
        except KeyError:
            return self.create_response(self._error(1), 400, "application/json")
        # Edit the listing based on information given
        listing = {
            "listing_id": listing_id
        }
        if "total" in event_body:
            listing["total"] = event_body["total"]
        if "name" in event_body:
            listing["name"] = event_body["name"]
        edited_listing = self.scoreboard_table.update_listing(self.DEFAULT_SCOREBOARD, listing=listing)
        return self.create_response(json.dumps(edited_listing), 200, "application/json")

    def edit_scoreboard(self, event, context):
        """
        Handler.edit_scoreboard

        Edit a scoreboard through a POST.
        Takes an AWS Lambda event with a valid authorization token and a body with data.
        """
        # Check for authorization then proceed
        cookie = self._parse_cookie(event['headers'])
        if not cookie or not self._check_auth(cookie):
            return self.create_response(self._error(4), 401, "application/json")
        # Load in the event body
        try:
            event_body = json.loads(event['body'])
        except KeyError:
            return self.create_response(self._error(1), 400, "application/json")
        # Edit the scoreboard based on information given
        kwargs = {}
        if "title" in event_body:
            kwargs["title"] = event_body["title"]
        edited_scoreboard = self.scoreboard_table.update_scoreboard(self.DEFAULT_SCOREBOARD, **kwargs)
        return self.create_response(json.dumps(edited_scoreboard), 200, "application/json")

    def delete_listing(self, event, context):
        """
        Handler.delete_listing

        Delete a listing to the selected scoreboard through a POST.
        Takes an AWS Lambda event with a valid authorization token and a body with data.
        """
        # Check for authorization then proceed
        cookie = self._parse_cookie(event['headers'])
        if not cookie or not self._check_auth(cookie):
            return self.create_response(self._error(4), 401, "application/json")
        # Load in the event body
        try:
            event_body = json.loads(event['body'])
            id = event_body["listing_id"]
        except KeyError:
            return self.create_response(self._error(1), 400, "application/json")
        # Delete the listing based on id
        deleted = self.scoreboard_table.delete_listing(self.DEFAULT_SCOREBOARD, id)
        response = {
            "success": deleted
        }
        return self.create_response(json.dumps(response), 200, "application/json")

    def static(self, event, context):
        filename = event["pathParameters"]["filename"]
        # Check for a backtrace in the filepath
        if '..' in filename:
            return self.create_response(self._error(5), 404, "application/json")
        # Open the file under the static directory
        with open("static/" + filename, 'r') as f_in:
            content = f_in.read()
        # Return the file contents and set the mimetype based on the file ending
        file_ending = filename.split('.')[-1]
        if file_ending in MIMETYPES:
            return self.create_response(content, 200, MIMETYPES[file_ending])
        else:
            return self.create_response(content, 200)

    def auth(self, event, context):
        # Parse the form data and get the username and password
        try:
            form_data = parse_qs(event["body"])
            username = str(form_data['username'][0])
            password = str(form_data['password'][0])
        except KeyError:
            return self.create_response(self._error(1), 400, "application/json")
        # Find the user based on username
        user = self.users_table.get_user(username)
        if user == None:
            return self.create_response(self._error(2), 400, "application/json")
        # And compare the password and password hash
        if not self.password_manager.compare(password, user['passhash']):
            return self.create_response(self._error(3), 401, "application/json")
        # Generate an auth token and return it to the user
        authorization = self.authorization_manager.generate_authorization(username)
        return self.create_response(json.dumps(authorization), 200, "application/json", [f"authToken={authorization['key']}; Secure", f"refreshToken={authorization['refresh_key']}; Secure", f"tokenExpires={authorization['expires']}; Secure", f"authUser={username}; Secure"])

    def _check_auth(self, cookie):
        # Get the auth token from the cookie and check it in the manager
        auth_token = cookie.get('authToken')
        if auth_token == None:
            return False
        return self.authorization_manager.check(auth_token.value)

    def _parse_cookie(self, headers):
        if "Cookie" in headers:
            data = headers["Cookie"]
            cookie = SimpleCookie(data)
            return cookie
        return False

    def create_response(self, content, code, content_type="text/html", cookies=None):
        response = {
            "statusCode": code,
            "body": content,
            "headers": {
                "Content-Type": content_type,
                "Access-Control-Allow-Credentials": True
            }
        }
        if cookies:
            if len(cookies) == 1:
                response["headers"]["Set-Cookie"] = cookie
            else:
                response["multiValueHeaders"] = {}
                response["multiValueHeaders"]["Set-Cookie"] = cookies
        return response

    def create_redirect(self, url):
        response = {
            "statusCode": 302,
            "headers": {
                "Location": url
            }
        }
        return response

    def _error(self, code):
        error = {
            "error": ERRORS[str(code)]["message"],
            "code": code
        }
        return json.dumps(error)

_inst = Handler()
index = _inst.index
edit = _inst.edit
auth = _inst.auth
add_listing = _inst.add_listing
edit_listing = _inst.edit_listing
edit_scoreboard = _inst.edit_scoreboard
delete_listing = _inst.delete_listing
static = _inst.static
