"""
Blueprint Note for Flask app Bot
handlers responsible for operations with Notebook
"""

# pylint: disable=W0614
# pylint: disable=W0401
# pylint: disable=E0402
# pylint: disable=R0801

# local packages
import os
import io
import sys
from flask import Blueprint, render_template, request, session, send_file

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

if __package__ == "" or __package__ is None:
    import global_var
    from contact_bp import *
    from file_data_classes import *
else:
    from . import global_var
    from .contact_bp import *
    from .file_data_classes import *

file_bp = Blueprint("file", __name__, url_prefix="/file")


@file_bp.route("/upload", methods=["GET", "POST"])
def upload():
    max_size = 10
    total_file = 100
    used_file = global_var.file_db.number_of_files(session['user_id'])
    if request.method == "POST":
        data = request.form.to_dict(flat=False)
        if "file" in request.files:
            file = request.files['file']
            result = global_var.file_db.insert_file(session['user_id'], file, max_size, total_file, used_file+1)
            if result == 0:
                return render_template("file/add_file_ok.html")
            return html_error(result)
    return render_template("file/file_to_upload.html",
                           max_size=max_size,
                           total_file=total_file,
                           used_file=used_file)


@file_bp.route("/download_file/<file_id>", methods=["POST"])
def download_by_id(file_id):
    if request.method == 'POST':
        file = global_var.file_db.get_file_by_id(file_id)
        with open (f"{session['user_id']}_temp_file.temp", 'wb') as temp:
            temp.write(file.file)
        return send_file(f"{session['user_id']}_temp_file.temp", download_name=file.name)


@file_bp.route("/delete/<file_id>", methods=["POST"])
def delete_by_id(file_id):
    if request.method == 'POST':
        result = global_var.file_db.delete_file(file_id)
        if result == 0:
            files = global_var.file_db.get_all_file_names(session['user_id'])
            return render_template("file/file_to_download.html", files=files)
        return html_error(result)


@file_bp.route("/download", methods=["POST", "GET"])
def download():
    if request.method == 'POST':
        file_type = request.form.get('file_type')
        if file_type == 'All types':
            file_type = None
    else:
        file_type = None
    files = global_var.file_db.get_all_file_names(session['user_id'], file_type)
    types = global_var.file_db.get_types(session['user_id'])
    return render_template("file/file_to_download.html", files=files, types=types)