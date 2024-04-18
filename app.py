#!/usr/bin/env python3

import os
import sys
import subprocess
import datetime
import random as random_module

from flask import Flask, render_template,render_template_string, request, redirect, url_for, make_response
import flask_login

# import logging
import sentry_sdk

# from markupsafe import escape
import pymongo
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
from dotenv import load_dotenv

# load credentials and configuration options from .env file
# if you do not yet have a file named .env, make one based on the template in env.example
load_dotenv(override=True)  # take environment variables from .env.

# instantiate the app using sentry for debugging
app = Flask(__name__)
app.secret_key = 'superb'

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

class User(flask_login.UserMixin):
    def __init__(self, name, password):
        self.id = name
        self.password = password

users = {"amigo": User("amigo", "adios")}

@login_manager.user_loader
def user_loader(id):
    return users.get(id)

# # turn on debugging if in development mode
# app.debug = True if os.getenv("FLASK_ENV", "development") == "development" else False

# try to connect to the database, and quit if it doesn't work
try:
    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]  # store a reference to the selected database

    # verify the connection works by pinging the database
    cxn.admin.command("ping")  # The ping command is cheap and does not require auth.
    print(" * Connected to MongoDB!")  # if we get here, the connection worked!
except ConnectionFailure as e:
    # catch any database errors
    # the ping command failed, so the connection is not available.
    print(" * MongoDB connection error:", e)  # debug
    sys.exit(1)  # this is a catastrophic error, so no reason to continue to live


# set up the routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    user = users.get(request.form["name"])

    if user is None or user.password != request.form["password"]:
        return redirect(url_for("login"))

    flask_login.login_user(user)
    return redirect(url_for("homepage"))

@app.route("/homepage")
@flask_login.login_required
def homepage():
    return render_template("home.html",logged= "Logged in as: "+flask_login.current_user.id)

@app.route("/browse")
def browse():
    docs = db.tinylibrary.find({}).sort("created_at", -1)
    
    return render_template("browse.html", docs=docs)

@app.route("/random")
def random():
    total_documents = db.tinylibrary.count_documents({})

    random_index = random_module.randint(0, total_documents - 1)
    random_document = db.tinylibrary.find().skip(random_index).limit(1)

    return render_template('random.html', random_document=random_document)

@app.route('/filter', methods=['GET'])
def filter():
    type_filter = request.args.get('media_type')
    status_filter = request.args.get('status')
    storage_filter = request.args.get('storage')

    storage_options = db.tinylibrary.distinct('storage')

    query = {}
    if type_filter:
        query['media_type'] = type_filter
    if status_filter:
        query['status'] = status_filter
    if storage_filter:
        query['storage'] = storage_filter

    filtered_docs = db.tinylibrary.find(query).sort("created_at", -1)

    return render_template('filter.html', docs=filtered_docs, storage_options=storage_options)

@app.route("/create")
def create():
    return render_template("create.html")  # render the create template


@app.route("/create", methods=["POST"])
def create_entry():
    media_type = request.form["media_type"]
    title = request.form["title"]
    storage = request.form["storage"]
    status = request.form["status"]
    notes = request.form["note"]

    doc = {"media_type": media_type,"title": title,"storage": storage,"status": status, "notes": notes, "created_at": datetime.datetime.utcnow()}
    db.tinylibrary.insert_one(doc)  # insert a new document

    return redirect(url_for("browse"))


@app.route("/edit/<mongoid>")
def edit(mongoid):
    doc = db.tinylibrary.find_one({"_id": ObjectId(mongoid)})
    return render_template("edit.html", mongoid=mongoid, doc=doc)


@app.route("/edit/<mongoid>", methods=["POST"])
def edit_entry(mongoid):
    media_type = request.form["media_type"]
    title = request.form["title"]
    storage = request.form["storage"]
    status = request.form["status"]
    notes = request.form["note"]

    doc = {
        # "_id": ObjectId(mongoid),
        "media_type": media_type,
        "title": title,
        "storage": storage,
        "status": status,
        "notes": notes,
    }

    db.tinylibrary.update_one(
        {"_id": ObjectId(mongoid)}, {"$set": doc}
    )

    return redirect(url_for("browse"))


@app.route("/delete/<mongoid>")
def delete(mongoid):
    db.tinylibrary.delete_one({"_id": ObjectId(mongoid)})

    return redirect(url_for("browse"))


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    GitHub can be configured such that each time a push is made to a repository, GitHub will make a request to a particular web URL... this is called a webhook.
    This function is set up such that if the /webhook route is requested, Python will execute a git pull command from the command line to update this app's codebase.
    You will need to configure your own repository to have a webhook that requests this route in GitHub's settings.
    Note that this webhook does do any verification that the request is coming from GitHub... this should be added in a production environment.
    """
    # run a git pull command
    process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
    pull_output = process.communicate()[0]
    # pull_output = str(pull_output).strip() # remove whitespace
    process = subprocess.Popen(["chmod", "a+x", "flask.cgi"], stdout=subprocess.PIPE)
    chmod_output = process.communicate()[0]
    # send a success response
    response = make_response(f"output: {pull_output}", 200)
    response.mimetype = "text/plain"
    return response


@app.errorhandler(Exception)
def handle_error(e):
    """
    Output any errors - good for debugging.
    """
    return render_template("error.html", error=e)  # render the edit template


# run the app
if __name__ == "__main__":
    # logging.basicConfig(filename="./flask_error.log", level=logging.DEBUG)
    app.run(load_dotenv=True)