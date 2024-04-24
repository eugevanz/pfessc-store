from flask import Flask, render_template
from supabase import create_client, Client
import os
import random

app = Flask(__name__)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route("/")
def hello_world():
    return render_template("index.html", title="Hello")
