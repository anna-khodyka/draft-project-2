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
import asyncio
from flask import Blueprint, render_template, request


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append(os.path.dirname(SCRIPT_DIR)+'news_feed')
if __package__ == "" or __package__ is None:
    import global_var
    from contact_bp import *
    from news_feed.app import get_feed
else:
    from . import global_var
    from .contact_bp import *
    from .news_feed.app import get_feed
news_bp = Blueprint("news", __name__, url_prefix="/news")


@news_bp.route("/get_news", methods=["GET"])
async def get_news():
    if request.method == "GET":
        feed = await get_feed(request)
        return render_template("news/get_news.html", feed=feed)
    return html_error("Here wouldn't be  method POST")


