# Scoreboard

A general scoreboard displayed on a web page for general purposes.

### Installation

Before installing, make sure you have all the prerequistes.
The following are all needed for basic instalation:

 + Git
 + AWS Account
 + Serverless
 + Python 3.8
 + Docker (only if not on Linux)

The next components are all optional but make for a better flow of the scoreboard.

 + Domain name with access to CNAMEs

To install the basic functional scoreboard download this repository.
There are two ways to do this.
Either download using the green code button at the top of the page on the right to download the ZIP.
Or, run `git clone https://github.com/PrestonHager/Scoreboard.git` in a terminal.
Setup an IAM user on your AWS account.
This can be any name, the important part to download is the keys.
<!-- TODO: there is a way to program these roles into the serverless.yml file
      then, we wouldn't need to add these permissions manually. -->
Additionally, add the following roles to this IAM user:

 + AmazonDynamoDBFullAccess
 + CloudFormationFullAccess
 + AWSLambda_FullAccess

Set your keys in the terminal through either of the following commands, replacing the example keys with the keys you downloaded earlier:

```bash
  export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
  export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

or

```bash
  serverless config credentials --provider aws --key AKIAIOSFODNN7EXAMPLE --secret wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

If you are not using a custom domain then comment out the last part of the `serverless.yml` file.
If you are on linux, you may not need to use docker to compile the dependencies.
Comment out the `python-requrements` portion of the `serverless.yml` file if you don't want to use docker.
Sometimes, it still won't work and you may get internal server errors (HTML 500), in this case, try redeploying it using the docker compiling.

Now, run `serverless deploy` in the terminal at the Scoreboard directory.
If all goes well, you should see a deployment and a url like the following in the output: `https://abcd1234ij.execute-api.us-east-1.amazonaws.com/dev/`.


### How it works

By using AWS's DynamoDB and Lambdas we create a webpage accessible scoreboard.
It is versatile in creating many scoreboards that can be displayed and edited.
First, the AWS Lambdas provide an access point for users to view and login to the scoreboards.
DynamoDB allows for quick and easy storage of the scoreboards.

### Development Notes

To test the lambda function without deploying, use a combination of the following.
Use `serverless invoke local -f {function name} -p {data path}` to invoke a function with specific data.
Use `serverless offline` to run an HTTP server on `localhost:3000` to test the HTML and css.
To compile the SASS files, run `sass -s compressed --no-source-map --watch static` to watch for changes made to the static `.scss` files.

### Contributing

Create any issues under the [GitHub page][0] for bugs or feature requests.
If you fix or improve any of these issues, commit a pull request.

[0]: https://github.com/PrestonHager/Scoreboard
