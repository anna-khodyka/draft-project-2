# home-work-16

Flask application 'Bot' - personal assistant with contact book and notebook features.

    To run:
    - set environmemt variable FLASK_APP=main.py:init_app()
    - set environmemt variable FLASK_ENV=development
    - run flask upp

Application modules are tested with Pytest. Pytest cov-report could be found at bot/test/cov-html folder. Average test coverage = 91%.

    Pytests running from test folder using:
    $ pytest --cov-config=.coveragerc --cov-report html:cov_html --cov=../

Pylint used for check through the code. From initial rank = -4.5 for the whole Project, the final Pylint rank reached at 10.0. Some warnings was disabled.

    Launched from root project folder with:
    $ pylint bot

    Disable list
    --disable=
    too-few-public-methods,
    ungrouped-imports,
    too-many-instance-attributes,
    broad-except,
    relative-beyond-top-level,
    undefined-variable,
    wildcard-import,
    unused-wildcard-import

All modules was formatted using Black. Seems almost fine, excepting chunks like this one:

    result = self.contact_db.aggregate(
                [
                    {
                        "$match": {
                            "$expr": {
                                "$in": [
                                    {
                                        "$substr": [
                                            {
                                                "$dateToString": {
                                                    "format": "%d.%m.%Y",
                                                    "date": "$birthday",
                                                }
                                            },
                                            0,
                                            5,
                                        ]
                                    },
                                    [
                                        (datetime.today() + timedelta(days=i)).strftime(
                                            "%d.%m.%Y"
                                        )[0:5]
                                        for i in range(1, period + 1)
                                    ],
                                ]
                            }
                        }
                    }
                ]
            )
