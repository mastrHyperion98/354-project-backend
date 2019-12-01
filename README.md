# 354TheStars - Marketplace

## Installation

### Python Virtual Environment (Recommended)

#### Create an environment

Create _venv_ folder within the project folder.

For Linux and Mac:

    $ cd 354-backend
    $ python3 -m venv venv

On Windows:

    > py -3 -m venv venv

#### Activate the environment

Before you work on the project, activate the corresponding environment.

For Linux and Mac:

    $ source venv/bin/activate

On Windows:

    > venv\Scripts\activate

#### Install the dependencies


    pip3 install -r requirements.txt

If you're on macOS you may run into an issue with the above command when it attempts to install psycopg2. For virtual environments psycopg2's installation needs to link against a non-native version of openssl.

To do this run:

    # This command assumes you have homebrew installed.
    brew install openssl

Then run:

    sudo env LDFLAGS="-I/usr/local/opt/openssl include -L/usr/local/opt/openssl/lib" pip3 install -r requirements.txt

### Running the application (Development environment only)

Note if you need to specify the origin for a CORS (Cross-Origin Resource Sharing). Note that the default origin is set to be a wildcard (*).

Then for Linux and Mac:

    $ export FLASK_ORIGIN=<origin>

For Windows:

    > set FLASK_ORIGIN=<origin>

For Linux and Mac:

    $ export FLASK_APP=flaskr
    $ export FLASK_ENV=development
    $ flask run

For Windows:

    > set FLASK_APP=flaskr
    > set FLASK_ENV=development
    > flask run

You will see an output similar to:

    * Serving Flask app "flaskr"
    * Environment: development
    * Debug mode: on
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    * Restarting with stat
    * Debugger is active!
    * Debugger PIN: 855-212-761


## Testing

Refer to README.md under _tests_
