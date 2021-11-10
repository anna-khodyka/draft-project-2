from datetime import date
import random
from werkzeug.security import check_password_hash, generate_password_hash
from flask import app
from faker import Faker

if __package__ == "" or __package__ is None:
    import db_postgres
    from SQL_alchemy_classes import *
    from users_data_classes import *
    from file_data_classes import *
else:
    from . import login_bp
    from .SQL_alchemy_classes import *
    from .users_data_classes import *
    from .file_data_classes import *

fake = Faker()

notes ={ 'Pytest': [
    """'#8414: pytest used to create directories under /tmp with world-readable permissions. 
    This means that any user in the system was able to read information written by tests 
    in temporary directories (such as those created by the tmp_path/tmpdir fixture). 
    Now the directories are created with private permissions.""",

    """ #8132: Fixed regression in approx: in 6.2.0 approx no longer raises TypeError 
    when dealing with non-numeric types, falling back to normal comparison. Before 6.2.0, 
    array types like tf.DeviceArray fell through to the scalar case, and happened to compare 
    correctly to a scalar if they had only one element. After 6.2.0, these types began failing, 
    because they inherited neither from standard Python number hierarchy nor from numpy.ndarray.""",

    """"#6909: Revert the change introduced by #6330, which required all arguments to 
    @pytest.mark.parametrize to be explicitly defined in the function signature. The intention of 
    the original change was to remove what was expected to be an unintended/surprising behavior, 
    but it turns out many people relied on it, so the restriction has been reverted."""],

    'Python':
        ["""Friday, November 5, 2021
Python 3.9.8 and 3.11.0a2 are now available
With the recent release of macOS 12 Monterey, we noticed that tkinter file dialogs are failing 
to show up on this new operating system, including in our built-in IDLE. Thanks to rapid help 
from the Tk team, and Marc Culler in particular, we were able to fix the issue by bundling 
Python 3.9.8 and Python 3.11.0a2 with a fixed Tcl/Tk version. 
""",

         """Python 3.9.8
         Get it here: https://www.python.org/downloads/release/python-398/
         Python 3.9.8 is the seventh maintenance release of the legacy 3.9 series. 
         Python 3.10 is now the latest feature release series of Python 3. Get the latest release of 3.10.x here.
         There’s been 202 commits since 3.9.7 which shows that there’s still considerable interest in improving Python 3.9. 
         To compare, at the same stage of the release cycle Python 3.8 received over 25% fewer commits. 
         See the changelog for details on what changed.""",

         """
         PEP-8 Tutorial: Code Standards in Python
         With this beginner tutorial, you'll start to explore PEP-8, Python's style guide, so that you 
         can start formatting your code correctly to maximize its readability!
         PEP-8 or the Python Enhancement Proposal presents some of the key points that you can use to 
         make your code more organized and readable. As Python creator Guido Van Rossum says:
         The code is read much more often than it is written.
         """,

         """Welcome to Faker’s documentation!
         Faker is a Python package that generates fake data for you. Whether you need to bootstrap 
         your database, create good-looking XML documents, fill-in your persistence to stress test 
         it, or anonymize data taken from a production service, Faker is for you.
         Faker is heavily inspired by PHP Faker, Perl Faker, and by Ruby Faker."""

         ],
    'HTML': [
        """Bootstrap Studio is a powerful desktop app for designing and prototyping websites.
    It comes with a large number of built-in components, which you can drag and drop to assemble 
    responsive web pages. The app is built on top of the hugely popular Bootstrap framework, 
    and exports clean and semantic HTML.""",

        """Is there a CSS documentation?
    Use this CSS reference to browse an alphabetical index of all of the standard CSS 
    properties, pseudo-classes, pseudo-elements, data types, functional notations and at-rules. 
    You can also browse key CSS concepts and a list of selectors organized by type. 
    Also included is a brief DOM-CSS / CSSOM reference.""",

        """ Knowledge Level Assumptions
        React is a JavaScript library, and so we’ll assume you have a basic understanding of 
        the JavaScript language. If you don’t feel very confident, we recommend going through 
        a JavaScript tutorial to check your knowledge level and enable you to follow along 
        this guide without getting lost. It might take you between 30 minutes and an hour, 
        but as a result you won’t have to feel like you’re learning both React and JavaScript at the same time."""
    ]
}

files = {"data/intents.json": ["intents.json"], "data/classes.pkl": ["classes.pkl"], "data/words.pkl": ["words.pkl"]}


def insert_users(session):
    users = [{'name': "Tatyana Filimonova", 'login': "Filimonova", 'password': "Filimonova", 'tag': 'Python'},
             {'name': "Natalya Solomko", 'login': "Solomko", 'password': "Solomko", 'tag': 'Scrum'},
             {'name': "Anna Khodyka", 'login': "Khodyka", 'password': "Khodyka", 'tag': 'Pytest'}]
    with session as connection:
        for i in range(0, len(users)):
            user = User_(username=users[i]['name'],
                         login=users[i]['login'],
                         password=generate_password_hash(users[i]['password']))
            session.add(user)
            session.commit()
            for _i in range(10):
                name = fake.first_name() + " " + fake.last_name()
                contact = Contact(name=name, birthday=
                fake.date(), created_at=date.today(), user_id=user.id)
                session.add(contact)
                session.commit()
                id = contact.contact_id
                try:
                    email = Email(email=fake.company_email(), contact_id=id)
                    session.add(email)
                    session.commit()
                except:
                    session.rollback()
                    print("scipped e-mail for user ID ", id)
                for p in range(random.randrange(0, 3, 1)):
                    try:
                        phone = Phone(phone=fake.msisdn(), contact_id=id)
                        session.add(phone)
                        session.commit()
                    except:
                        session.rollback()
                        print("scipped phone for user ID ", id)
                try:
                    country = fake.country()
                    if len(country) > 50:
                        country = country[:50]
                    address = Address(zip=fake.postcode(),
                                       city=fake.city(),
                                       country=country,
                                       street=fake.street_name(),
                                       region="",
                                       house=fake.building_number(),
                                       apartment=random.randrange(1, 100, 1),
                                       contact_id=id)
                    session.add(address)
                    session.commit()
                except:
                    session.rollback()
                    print("scipped address for user ID ", id)

            for key in notes.keys():
                for k in range(0, len(notes[key])):
                    try:
                        note = Note(text=notes[key][k],
                                    user_id=user.id
                                    )
                        session.add(note)
                        session.commit()
                        tag = Tag(tag=key, user_id=user.id)
                        session.add(tag)
                        session.commit()
                        tag_and_note = TagsAndNotes(tag_id=tag.tag_id, note_id=note.note_id)
                        session.add(tag_and_note)
                        session.commit()
                    except:
                        session.rollback()
                        print("Skipped note")
                        continue
            try:
                for key in files.keys():
                    folder = FileFolderPSQL(session)
                    file_type='Other'
                    with open(key, 'br') as file:
                        ext = files[key][0].rsplit('.', 1)[1].lower()
                        for key_ in extensions_.keys():
                            if ext.upper() in extensions_[key_]:
                                file_type = key.capitalize()
                        file = File(
                            user_id=user.id,
                            name=files[key][0],
                            file_date=datetime.now(),
                            file_length=100,
                            file_type=file_type,
                            file=file.read()
                        )
                        session.add(file)
                        session.commit()
            except Exception as error:
                print(error)
                session.rollback()


if __name__ == '__main__':
    engine = create_engine("postgresql+psycopg2://postgres:1234@localhost/contact_book")
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base.metadata.bind = engine
    insert_users(session)


