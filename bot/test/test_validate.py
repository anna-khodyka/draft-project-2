"""
Testing validator for contact add- and edit- handlers
"""

#pylint: disable=W0614
#pylint: disable=W0612
#pylint: disable=W0401
#pylint: disable=C0413

import pytest
import sys
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append('../')
if True:
    from validate import *

phones = ['099-070-090-90', '099&9/08887+090-0', '90()899-83 0000']


@pytest.mark.parametrize('phone_list', phones)
def test_clean_phone_str(phone_list):
    """
    Testing phone string cleaner
    :param phone_list: fixture
    :return:
    """
    res = clean_phone_str(phone_list)
    assert res.isdigit() is True


names = ['', '*' * 51, 34, None, False]


@pytest.mark.parametrize('name', names)
def test_name_checker(name):
    """
    Testing name validator
    :param name: fixture
    :return:
    """
    valid, error, name_ = name_checker(name)
    assert valid is False


birthdays = ['7' * 51, '1900-00-00', '1900-15-15']


@pytest.mark.parametrize('birthday', birthdays)
def test_birthday_checker(birthday):
    """
    Testing birthday validator
    :param birthday: fixture
    :return:
    """
    valid, error, birthday_ = birthday_checker(birthday)
    assert valid is False


zips = ['7' * 51, 'dsfdsf', '(090)00', False]


@pytest.mark.parametrize('zip_code', zips)
def test_zip_checker(zip_code):
    """
    Testing zip validator
    :param zip_code: fixture
    :return:
    """
    valid, error, zip_ = zip_checker(zip_code)
    assert valid is False


countries = [None, 'a' * 51, 900, False, 'ar%%ar', "*awar$", ]


@pytest.mark.parametrize('country', countries)
def test_country_checker(country):
    """
    Testing country validator
    :param country: fixture
    :return:
    """
    valid, error, country_ = country_checker(country)
    assert valid is False


@pytest.mark.parametrize('region', countries)
def test_region_checker(region):
    """
    Testing region validator
    :param region: fixture
    :return:
    """
    valid, error, region_ = region_checker(region)
    assert valid is False
    if isinstance(region_, str):
        assert re.search(r'[^a-zA-Z\-]', region_) is None
        assert len(region_) != 0


@pytest.mark.parametrize('city', countries)
def test_city_checker(city):
    """
    Testing city validator
    :param city: fixture
    :return:
    """
    valid, error, city_ = city_checker(city)
    assert valid is False
    if isinstance(city_, str):
        assert re.search(r'[^a-zA-Z\-]', city_) is None


@pytest.mark.parametrize('street', countries)
def test_street_checker(street):
    """
    Testing street validator
    :param street: fixture
    :return:
    """
    valid, error, street_ = street_checker(street)
    assert valid is False
    if isinstance(street_, str):
        assert re.search(r'[^a-zA-Z\-]', street_) is None


houses = [None, 'a' * 12, 12133900, False, '&arar', "*awar$", ]


@pytest.mark.parametrize('house', houses)
def test_house_checker(house):
    """
    Testing house validator
    :param house: fixture
    :return:
    """
    valid, error, house_ = house_checker(house)
    assert valid is False
    valid, error, house_ = house_checker('12-a')
    assert valid is True
    valid, error, house_ = house_checker('123a')
    assert valid is True


@pytest.mark.parametrize('apartment', houses)
def test_apartment_checker(apartment):
    """
    Testing apartment validator
    :param apartment: fixture
    :return:
    """
    valid, error, apartment_ = apartment_checker(apartment)
    assert valid is False
    valid, error, apartment_ = apartment_checker('12-a')
    assert valid is True
    valid, error, apartment_ = apartment_checker('123a')
    assert valid is True
