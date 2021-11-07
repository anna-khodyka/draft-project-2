# pylint: disable=E0402
# pylint: disable=W0611
# pylint: disable=C0412
# pylint: disable=R0801

"""
Blueprint 'contact' of Flask project 'Bot'
Contains all routes for contact_book

"""


# global packages
import os
import sys
import copy
from datetime import datetime
from flask import Blueprint, render_template, request, abort, session


# local packages
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
if __package__ == "" or __package__ is None:
    from contacts_data_classes import (
        ContactbookPSQL,
        ContactDetails,
        ContactPSQL,
        ContactDict,
    )
    from validate import validate_contact_data, form_dict_temp
    import global_var
else:
    from .contacts_data_classes import (
        ContactbookPSQL,
        ContactDetails,
        ContactPSQL,
        ContactDict,
    )
    from .validate import validate_contact_data, form_dict_temp
    from . import global_var

contact_bp = Blueprint("contact", __name__, url_prefix="/contact")


def clean_search_str(keywords):
    """
    Clean the user input str from special characters which could have negative impact when searching
    :param keywords:
    :return:
    """
    keywords = (
        keywords.replace("+", r"\+")
        .replace("*", r"\*")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("[", r"\[")
        .replace("]", r"\]")
        .replace("?", r"\?")
        .replace("$", r"\$")
        .replace(r"'\'", r"\\")
    )
    return keywords


def html_error(error):
    """
    Render the HTML page in case of error in application
    :param error: str
    :return: rendered HTML
    """
    return render_template("error.html", error=error)


def get_period(message=""):
    """
    Prepare web form to input the period wich be used to find nearest new-borners
    :param message: str
    :return: rendered HTML
    """
    return render_template("contact/get_period.html", err_message=message)


@contact_bp.route("/add_contact", methods=["GET", "POST"])
def add_contact():
    """
    Add new contact to contact book
    GET - prepare the web form to get contact data
    POST - validate data from web form and save contact to DB
    :return: rendered HTML
    """
    form_dict = copy.deepcopy(form_dict_temp)
    if request.method == "POST":
        form_dict = validate_contact_data(request, form_dict)
        valid_list = [element["valid"] for element in form_dict.values()]
        if False not in valid_list:
            res = global_var.contact_book.insert_contact(session['user_id'], ContactDict(form_dict))
            if res == 0:
                return render_template("contact/add_contact_OK.html")
            return html_error(res)
    return render_template("contact/add_contact.html", form_dict=form_dict)


@contact_bp.route("/edit_contact", methods=["GET", "POST"])
def edit_contact():
    """
    Find and select contact for edit contact details
    GET - prepare web form for search a contact
    POST - find the contact by specified keywords and represent the list of them
    :return: rendered HTML
    """
    results = []
    if request.method == "POST":
        data = request.form.to_dict(flat=False)
        if "Keywords" not in data:
            abort(400, "Wrong request data")
        keywords = clean_search_str(request.form.get("Keywords"))
        for k in list(keywords.strip().split(" ")):
            result = global_var.contact_book.get_contacts(session['user_id'], k)
            if isinstance(result, str):
                return html_error(result)
            results.extend(result)
            return render_template("contact/contact_found.html", result=results)
    else:
        return render_template("contact/find_contact.html")


@contact_bp.route("/edit_contact/<contact_id>", methods=["GET", "POST"])
def edit_contact_(contact_id):
    """
    Edit contact defined by contact_id
    GET - prepare web-form for edit contact details
    PATH - validate and save data to DB
    :param contact_id: integer
    :return: rendered HTML
    """
    form_dict = copy.deepcopy(form_dict_temp)
    if request.method == "POST":
        data = request.form.to_dict(flat=False)
        for key in form_dict_temp:
            if key not in data:
                abort(400, "Wrong request data")
        form_dict = validate_contact_data(request, form_dict)
        valid_list = [val["valid"] for val in form_dict.values()]
        if False not in valid_list:
            res = global_var.contact_book.update_contact(
                contact_id, ContactDict(form_dict)
            )
            if res == 0:
                return render_template("contact/edit_contact_OK.html")
            return html_error(res)

    else:
        contact = global_var.contact_book.get_contact_details(contact_id)
        if isinstance(contact, str):
            return html_error(contact)
        form_dict["Name"]["value"] = contact.name
        form_dict["Birthday"]["value"] = (
            datetime.strptime(contact.birthday, "%d.%m.%Y") if contact.birthday else ""
        )
        form_dict["Email"]["value"] = contact.email
        form_dict["Phone"]["value"] = ", ".join(list(contact.phone))
        form_dict["ZIP"]["value"] = contact.zip
        form_dict["Country"]["value"] = contact.country
        form_dict["Region"]["value"] = contact.region
        form_dict["City"]["value"] = contact.city
        form_dict["Street"]["value"] = contact.street
        form_dict["House"]["value"] = contact.house
        form_dict["Apartment"]["value"] = contact.apartment
    return render_template("contact/edit_contact.html", form_dict=form_dict)


@contact_bp.route("/find_contact", methods=["GET", "POST"])
def find_contact():
    """
    Find the contacts in contact_book by specified list of keywords.
    Search for field Name and Phone, so phone number or part of it could be used
    GET - prepare form for keyword request
    POST - search by specified keywords and represent the results
    :return: rendered HTML
    """
    results = []
    if request.method == "POST":
        data = request.form.to_dict(flat=False)
        if "Keywords" not in data:
            abort(400, "Wrong request data")
        keywords = clean_search_str(request.form.get("Keywords"))
        for k in list(keywords.strip().split(" ")):
            for res in global_var.contact_book.get_contacts(session['user_id'], k):
                if isinstance(res, str):
                    return html_error(res)
                if res not in results:
                    results.append(res)
        return render_template("contact/contact_found.html", result=results)
    return render_template("contact/find_contact.html")


@contact_bp.route("/show_all_contacts", methods=["GET"])
def show_all_contacts():
    """
    Return the list of all contacts from the contact_book.
    :return: rendered HTML
    """
    result = global_var.contact_book.get_all_contacts(session['user_id'])
    if isinstance(result, str):
        return html_error(result)
    return render_template("contact/all_contacts.html", result=result)


@contact_bp.route("/contact_detail/<contact_id>", methods=["GET", "POST"])
def contact_detail(contact_id):
    """
    Return repesentation of contact details. Contact specified by param contact_id
    :param contact_id: int
    :return: rendered HTML
    """
    contact = global_var.contact_book.get_contact_details(contact_id)
    if isinstance(contact, str):
        return html_error(contact)
    return render_template(
        "contact/contact_details.html",
        contact=contact,
        phone=contact.phone,
        email=contact.email,
        address=contact,
        url="/find_contact",
    )


@contact_bp.route("/next_birthday", methods=["GET", "POST"])
def next_birthday():
    """
    Find all the new-borners in the period defined by user
        GET - return form to define a period
        POST - return  the list of new-borners in specified period
    :return: rendered HTMl
    """
    if request.method == "POST":
        try:
            period = int(request.form.get("Period"))
            assert 0 < period < 365
        except (ValueError, AssertionError):
            return get_period(
                "You could use numbers only, the period should be > 0 and < 365"
            )
        res = global_var.contact_book.get_birthday(session['user_id'], period)
        if isinstance(res, str):
            return html_error(res)
        return render_template(
            "contact/birthday_contact_found.html",
            days=request.form.get("Period"),
            result=res,
        )
    return get_period()


@contact_bp.route("/delete_contact", methods=["GET", "POST"])
def delete_contact():
    """
    Searching and selecting for delete a contact in contact_book
    GET - prepare form for search contact
    POST - searching and representing the results, to select a contact to be deleted
    """
    results = []
    if request.method == "POST":
        data = request.form.to_dict(flat=False)
        if "Keywords" not in data:
            abort(400, "Wrong request data")
        keywords = clean_search_str(request.form.get("Keywords"))
        for k in list(keywords.strip().split(" ")):
            res = global_var.contact_book.get_contacts(session['user_id'], k)
            if isinstance(res, str):
                return html_error(res)
            results.extend(res)
        return render_template("contact/contact_to_delete.html", result=results)
    return render_template("contact/search_contact_to_delete.html")


@contact_bp.route("/delete_contact/<contact_id>", methods=["GET", "POST"])
def contact_delete_(contact_id):
    """
    delete contact from contact_book by
    :param contact_id: integer
    :return: HTMl with OK result or with error message
    """
    res = global_var.contact_book.delete_contact(contact_id)
    if res == 0:
        return render_template("contact/contact_delete_OK.html", id=contact_id)
    return html_error(res)


@contact_bp.route("/delete_contacts", methods=["POST"])
def delete_contacts():
    contact_ids = request.form.getlist("Delete")
    for contact_id in contact_ids:
        res = global_var.contact_book.delete_contact(contact_id)
        if res != 0:
            return html_error(res)
    return render_template("contact/contact_delete_OK.html", id=contact_ids)