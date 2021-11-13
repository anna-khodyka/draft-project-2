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
import sys
import re
from flask import Blueprint, render_template, request, redirect
from markupsafe import Markup

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

if __package__ == "" or __package__ is None:
    import global_var
    from contact_bp import *
else:
    from . import global_var
    from .contact_bp import *


note_bp = Blueprint("note", __name__, url_prefix="/note")


@note_bp.route("/find_notes", methods=["GET", "POST"])
def find_notes():
    """
    Search for notes in Notebook
    GET - prepare search form
    POST - make search by keywords from web form and represent the results.
    Search through Text and Keywords fields
    :return: rendered HTML
    """
    results = []
    if request.method == "POST":
        data = request.form.to_dict(flat=False)
        if "Keywords" not in data:
            abort(400, "Wrong request data")
        keywords = clean_search_str(request.form.get("Keywords"))
        for k in [kw.strip() for kw in keywords.split(",")]:
            for res in global_var.note_book.get_notes(session['user_id'], k):
                if isinstance(res, str):
                    return html_error(res)
                if res not in results:
                    regex = fr"(?P<to_subst>{k}[\w]*[\ ]?[$]?)"
                    subst = r"<mark style='background-color: #34d8eb;'>\g<to_subst></mark>"
                    res.text = Markup(re.sub(regex, subst, res.text, 0, re.MULTILINE | re.I))
                    results.append(res)

        return render_template("note/find_notes_found.html", result=results)
    tags = global_var.note_book.get_all_tags(session['user_id'])
    return render_template("note/find_notes_search.html", tags=tags)


@note_bp.route("/find_notes/<tag>/<target>", methods=["GET", "POST"])
def find_notes_by_tag(tag, target):
    results = global_var.note_book.get_notes_by_tag(session['user_id'], tag)
    if isinstance(results, str):
        return html_error(results)
    for i in range(0, len(results)):
        regex = fr"(?P<to_subst>{tag}[\w]*[\ ]?[$]?)"
        subst = r"<mark style='background-color: #34d8eb;'>\g<to_subst></mark>"
        results[i].text = Markup(re.sub(regex, subst, results[i].text, 0, re.MULTILINE | re.I))
    if target in ['find', 'edit']:
        return render_template("note/find_notes_found.html", result=results)
    elif target in ['delete']:
        return render_template("note/delete_notes_found.html", result=results)

@note_bp.route("/add_tag", methods=["GET", "POST"])
def create_tag():
    print("TRY TO CREATE TAG - START")
    res = global_var.note_book.create_tag(session['user_id'],
                                          session['current_note'],
                                          request.form.get("new_tag")
                                          )
    if isinstance(res, str):
        return html_error(res)
    if session['current_note']:
        return redirect(f"save_note/{session['current_note']}")
    else:
        return redirect("add_note")



@note_bp.route("/show_all_notes", methods=["GET"])
def show_all_notes():
    """
    Show all the Notes from Notebook
    :return: rendered HTML
    """
    result = global_var.note_book.get_all_notes(session['user_id'])
    if isinstance(result, str):
        return html_error(result)
    return render_template("note/all_notes.html", result=result)


@note_bp.route("/add_note", methods=["GET", "POST"])
def add_note():
    """
    Add new note to DB
    GET - prepare the web form for user to input Note data - Text and keywords
    POST - saving data from web form and save Note to DB
    :return:
    """
    if request.method == "POST":
        data = request.form.to_dict(flat=False)
        if "Text" not in data:
            abort(400, "Wrong request data")
        text = request.form.get("Text")
        if len(text) > 500:
            text = text[0:500]
        res = global_var.note_book.insert_note(
            session['user_id'],
            request.form.getlist("Tags"),
            text
        )
        if res == 0:
            return render_template("note/add_note_OK.html")
        return html_error(res)
    session['current_note'] = 0
    tags = global_var.note_book.get_all_tags(session['user_id'])
    return render_template("note/add_note.html", tags=tags)


@note_bp.route("/edit_note", methods=["GET", "POST"])
def edit_note():
    """
    Prepare the list of the Note that user would like to update
    GET - prepare the we form for user input
    POST - search notes using user input and represent the results
    :return: rendered HTML
    """
    results = []
    if request.method == "POST":
        data = request.form.to_dict(flat=False)
        if "Keywords" not in data:
            abort(400, "Wrong request data")
        keywords = clean_search_str(request.form.get("Keywords"))
        for k in [kw.strip() for kw in keywords.split(",")]:
            for res in global_var.note_book.get_notes(session['user_id'], k):
                if res not in results:
                    results.append(res)
        return render_template("note/find_notes_found.html", result=results)
    tags = global_var.note_book.get_all_tags(session['user_id'])
    return render_template("note/find_notes_search.html", tags=tags)


@note_bp.route("/save_note/<note_id>", methods=["GET", "POST"])
def save_note(note_id):
    """
    Save updated Note by note_id with data from web form dict {'Keywords':, 'Text':}
    GET - prepare web form to edit Note selected by ID
    POST - update note selected by ID with web form data
    :param note_id: int
    :return: rendered HTML
    """
    if request.method == "POST":
        data = request.form.to_dict(flat=False)
        if "Tags" not in data or "Text" not in data:
            abort(400, "Wrong request data")
        text = request.form.get("Text")
        if len(text) > 500:
            text = text[0:500]
        res = global_var.note_book.update_note(
            note_id, request.form.getlist("Tags"), text)
        if res == 0:
            return render_template("note/edit_notes_OK.html")
        return html_error(res)
    tags = global_var.note_book.get_all_tags(session['user_id'])
    result = global_var.note_book.get_note_by_id(note_id)
    session['current_note'] = note_id
    return render_template("note/edit_notes_save.html", res=result, tags=tags)


@note_bp.route("/delete_note", methods=["GET", "POST"])
def delete_note():
    """
    Make a preparations to delete a Note from DB
    GET - create a from to search a Note which user would like to delete
    POST - search Note by user put in Keywords and do the representation of search resuls.
    Search made by Note and keywords fields
    :return: rendered HTML
    """
    results = []
    if request.method == "POST":
        data = request.form.to_dict(flat=False)
        if "Keywords" not in data:
            abort(400, "Wrong request data")
        keywords = clean_search_str(request.form.get("Keywords"))
        for k in [kw.strip() for kw in keywords.split(",")]:
            for res in global_var.note_book.get_notes(session['user_id'], k):
                if isinstance(res, str):
                    return html_error(res)
                if res not in results:
                    results.append(res)
        return render_template("note/delete_notes_found.html", result=results)
    tags = global_var.note_book.get_all_tags(session['user_id'])
    return render_template("note/delete_notes_search.html", tags=tags)


@note_bp.route("/delete_note/<note_id>", methods=["GET", "POST"])
def note_delete_(note_id):
    """
    Delete Note from notebook by given note_id
    :param note_id:
    :return: rendered HTML
    """
    res = global_var.note_book.delete_note(note_id)
    if res == 0:
        return render_template("note/delete_notes_OK.html", id=note_id)
    return html_error(res)


@note_bp.route("/delete_notes", methods=["POST"])
def delete_notes():
    note_ids = request.form.getlist("Delete")
    for note_id in note_ids:
        res = global_var.note_book.delete_note(note_id)
        if res != 0:
            return html_error(res)
    return render_template("note/delete_notes_OK.html", id=note_ids)
