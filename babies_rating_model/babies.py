import imghdr
import os
from pathlib import Path

import joblib
import pandas as pd
from flask import (
    Blueprint,
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
)
from flask import session as fsession
from flask import url_for
from werkzeug.utils import secure_filename

from flask_session import Session

from . import data
from .tools import download_data


class Config:
    SECRET_KEY = "akdakdsfahsdf"
    SESSION_TYPE = "filesystem"
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    UPLOAD_EXTENSIONS = [".xlsx", ".csv"]
    UPLOAD_PATH = "uploads"


app = Flask(__name__)
app.config.from_object(Config)
session = Session(app)


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    f_format = imghdr.what(None, header)
    if not f_format:
        return None
    return "." + (f_format if f_format != "xlsx" else "csv")


@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413


@app.route("/")
def index():
    files = os.listdir(app.config["UPLOAD_PATH"])
    return render_template("view.html", files=files)


@app.route("/", methods=["GET", "POST"])
def upload_file():
    uploaded_file = request.files["file"]
    filename = secure_filename(uploaded_file.filename)
    if filename != "":
        _, extension = tuple(filename.split("."))
        filename = "data" + "." + extension
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
            return "Invalid file", 400
        if request.method == "POST":
            uploaded_file.save(os.path.join(app.config["UPLOAD_PATH"], filename))
            if filename.endswith("xlsx"):
                df_data = pd.read_excel(
                    Path(__file__).parent.parent / "uploads/data.xlsx"
                )
            else:
                df_data = pd.read_csv(Path(__file__).parent.parent / "uploads/data.csv")

            model = joblib.load(Path(__file__).parent / "model.pkl")
            vectorizer = joblib.load(Path(__file__).parent / "vectorizer.pkl")
            df_data.loc[:, "predicted_rating"] = df_data.review.apply(
                lambda txt: model.predict(
                    vectorizer.transform([data.preprocessing(txt)])
                )[0]
                if isinstance(txt, str)
                else None
            )
            df_data["predicted_rating"] = df_data["predicted_rating"].map(
                {1.0: str(1), 0.0: str(0)}
            )
            fsession["data"] = df_data
            return render_template("prediction.html", df_data=df_data.head(30))
    return "", 204


@app.route("/uploads/<filename>")
def upload(filename):
    return send_from_directory(app.config["UPLOAD_PATH"], filename)


@app.route("/download_data", methods=("POST", "GET"))
def predicted_data():
    s_data = fsession.get("data")
    return download_data(dataframe=s_data, attachment_filename="predicted_data.xlsx")
