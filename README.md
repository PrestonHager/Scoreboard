# Scoreboard

A general scoreboard displayed on a web page for general purposes.

### Installation

Before installing, make sure you have all the prerequistes.
The following are all needed for basic instalation:

 + Git
 + AWS Account
 + Serverless
 + Python 3.8

The next components are all optional but make for a better flow of the scoreboard.

 + Domain name with access to CNAMEs

To install the basic functional scoreboard download this repository.
There are two ways to do this.
Either download using the green code button at the top of the page on the right.
Or, run `git clone https://github.com/PrestonHager/Scoreboard.git` in a terminal.
Now, run `sls deploy` in the terminal at the Scoreboard directory.

### How it works

By using AWS's DynamoDB and Lambdas we create a webpage accessible scoreboard.
It is versatile in creating many scoreboards that can be displayed and edited.
First, the AWS Lambdas provide an access point for users to view and login to the scoreboards.
DynamoDB allows for quick and easy storage of the scoreboards.

### Contributing

Create any issues under the [GitHub page][0] for bugs or feature requests.
If you fix or improve any of these issues, commit a pull request.

[0]: https://github.com/PrestonHager/Scoreboard
