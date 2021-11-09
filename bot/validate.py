"""
Input validation for edit and add contact views

"""

from datetime import datetime
import re


def clean_phone_str(phone):
    """
    Clean string from web form which would be used for phone number
    :param phone: str
    :return: phone: str
    """
    phone = (
        phone.replace("-", "")
        .replace("{", "")
        .replace("}", "")
        .replace("[", "")
        .replace("]", "")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace(" ", "")
        .replace("+", "")
        .replace("*", "")
        .replace("&", "")
        .replace(r"/", "")
    )
    return phone


def validate_contact_data(request, form_dict):
    """
    Validate data end return to view dictionary with data end|or errors
    :param request: flask.request
    :param form_dict: dictionary with validation params
    :return: dictionary with validated data
    """
    for key in form_dict.keys():
        if re.search(r"^Hint", request.form.get(key)):
            form_dict[key]["value"] = ""
        else:
            form_dict[key]["value"] = request.form.get(key)
        res_tuple = form_dict[key]["checker"](form_dict[key]["value"])
        form_dict[key]["valid"] = res_tuple[0]
        form_dict[key]["error_message"] = res_tuple[1]
        form_dict[key]["value"] = res_tuple[2]
    return form_dict


def name_checker(name):
    """
    check the Name field from request
    :param name: str
    :return: valid: boolean, error: str, name: str
    """

    error_message = ""
    valid = True
    if not isinstance(name, str):
        error_message = "Name should be str"
        valid = False
    elif len(name) > 50:
        error_message = "Max len of Name is 50 char"
        valid = False
    elif name == "":
        error_message = "Name have to be at least one symbol "
        valid = False
    return valid, error_message, name


def birthday_checker(birthday):
    """
    check the birthday field from request
    :param birthday: str
    :return: valid: boolean, error: str, birthday: datetime
    """
    if not isinstance(birthday, str):
        valid = False
    if birthday == "":
        valid = True
    elif re.search(r"\d{4}\-\d{2}\-\d{2}", birthday) is None:
        valid = False
    else:
        try:
            birthday = datetime.strptime(birthday, "%Y-%m-%d")
            valid = True
        except ValueError:
            valid = False
    error_message = (
        "" if valid is True else f"Format should be YYYY-mm-dd, but used  {birthday}"
    )
    return valid, error_message, birthday


def phone_checker(phones):
    """
    Check the phones field from request
    :param phones: str
    :return: valid: boolean, error: str, phones: str
    """
    error_message = ""
    valid = True
    if phones:
        phones = clean_phone_str(phones)
        for phone in phones.split(","):
            if re.search(r"\+{0,1}\d{9,13}", phone.strip()) is None:
                error_message = (
                    """Phones format: '[+] XXXXXXXXXXXX'"""
                    + """'(9-12 dig.), separated by ','"""
                )
                valid = False
    return valid, error_message, phones


def zip_checker(zip_code):
    """
    Check the zip field from request
    :param zip_code: str
    :return: valid: boolean, error: str, zip_code: str
    """
    print("-" * 10)
    print(zip_code)
    error_message = ""
    valid = True
    if not isinstance(zip_code, str):
        valid = False
    elif zip_code == "":
        valid = True
    elif len(zip_code) > 10:
        error_message = "Max len of ZIP is 10 char"
        valid = False
    elif not zip_code.isdigit():
        error_message = "ZIP could contain only numbers"
        valid = False
    return valid, error_message, zip_code


def country_checker(country):
    """
    Check the country field from request
    :param country: str
    :return: valid: boolean, error: str, country: str
    """
    return str_check(country, 50, "Country")


def region_checker(region_):
    """
    Check the region field from request
    :param region_: str
    :return: valid: boolean, error: str, region_: str
    """
    return str_check(region_, 50, "Region")


def city_checker(city):
    """
    Check the city field from request
    :param city: str
    :return: valid: boolean, error: str, city: str
    """

    return str_check(city, 40, "City")


def str_check(str_, len_, name):
    """
    Used to validate text fields
    :param str_: str, len_: int, name: str
    :return: valid: boolean, error: str, str_: str
    """
    valid = True
    error_message = ""
    if not isinstance(str_, str):
        valid = False
        error_message = f"{name} should be string"
    elif len(str_) > len_:
        str_ = str_[:len_]
        error_message = f"Max len of {name} is {len_} char"
        valid = False
    elif str_ == "":
        valid = True
        error_message = ""
    elif re.search(r"[^a-zA-Zа-яА-ЯіІїЇєЄ\-0-9\ \.\,\(\)\'\"\&]", str_):
        error_message = f"{name} should not contain any special characters"
        str_ = re.sub(r"[^a-zA-Zа-яА-ЯіІїЇєЄ\-0-9\ \.\,\(\)\'\"\&]", "", str_)
        valid = False
    return (valid, error_message, str_)


def number_check(num_, len_, name):
    """
    Check the num fields from request
    :param num_: str
    :return: valid: boolean, error: str, street: num_
    """
    valid = True
    error_message = ""
    if not isinstance(num_, str):
        valid = False
        error_message = f"Input for {name} should be string"
    elif len(num_) > len_:
        error_message = f"Max len of {name} is 5 char"
        valid = False
    elif num_ == "":
        valid = True
        error_message = ""
    elif not re.search(r"[\d]+[-\/.]*[a-zA-Zа-яА-Я]*", num_):
        error_message = f"{name} should be: [0-9][ - . /][ a-zA-Z]"
        valid = False
    return (valid, error_message, num_)


def street_checker(street):
    """
    Check the street field from request
    :param street: str
    :return: valid: boolean, error: str, street: str
    """
    return str_check(street, 50, "Street")


def house_checker(house):
    """
    Check the house field from request
    :param house: str
    :return: valid: boolean, error: str, house: str
    """
    return number_check(house, 5, "House")


def apartment_checker(apartment):
    """
    Check the apartment field from request
    :param apartment: str
    :return: valid: boolean, error: str, apartment: str
    """
    return number_check(apartment, 5, "Apartment")


def email_checker(email):
    """
    Check the email field from request
    :param email: str
    :return: valid: boolean, error: str, email: str
    """
    error_message = ""
    valid = True
    if email != "":
        if (
            re.search(r"[a-zA-Z0-9\.\-\_]+@[a-zA-Z0-9\-\_\.]+\.[a-z]{2,4}", email)
            is None
        ):
            error_message = (
                "Email should have format: 'name@domain.[domains.]high_level_domain'"
            )
            valid = False
    return valid, error_message, email


form_dict_temp = {
    "Name": {
        "value": "",
        "valid": True,
        "checker": name_checker,
        "error_message": "",
    },
    "Birthday": {
        "value": "",
        "valid": True,
        "checker": birthday_checker,
        "error_message": "",
    },
    "Email": {
        "value": "",
        "valid": True,
        "checker": email_checker,
        "error_message": "",
    },
    "Phone": {
        "value": "",
        "valid": True,
        "checker": phone_checker,
        "error_message": "",
    },
    "ZIP": {
        "value": "",
        "valid": True,
        "checker": zip_checker,
        "error_message": "",
    },
    "Country": {
        "value": "",
        "valid": True,
        "checker": country_checker,
        "error_message": "",
    },
    "Region": {
        "value": "",
        "valid": True,
        "checker": region_checker,
        "error_message": "",
    },
    "City": {
        "value": "",
        "valid": True,
        "checker": city_checker,
        "error_message": "",
    },
    "Street": {
        "value": "",
        "valid": True,
        "checker": street_checker,
        "error_message": "",
    },
    "House": {
        "value": "",
        "valid": True,
        "checker": house_checker,
        "error_message": "",
    },
    "Apartment": {
        "value": "",
        "valid": True,
        "checker": apartment_checker,
        "error_message": "",
    },
}
