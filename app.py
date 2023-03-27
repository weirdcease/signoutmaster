from flask import Flask
import os
from datetime import datetime

import setup
from signout import signout

# This version of app.py is designed to run the app locally. The app is contained within a blueprint, and this is done so that the same code can be run standalone as well as from my server.

app = Flask(__name__, subdomain_matching=True)
app.config["SECRET_KEY"] = os.urandom(12).hex()

app.register_blueprint(signout)

def time(timestamp, template = "%m/%d/%y(%a)%H:%M:%S"):
    return datetime.fromtimestamp(timestamp).strftime(template)

app.add_template_filter(time)

if __name__ == "__main__":
    app.run()