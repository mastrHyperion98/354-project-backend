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


    pip install requirements.txt

### Running the application (Development environment only)

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
