# draft-project-2

Data for database stored in https://github.com/TatyanaFilimonova/draft-project-2/blob/main/bot/dump-contact_book-202111031759

Just create contact_book database in DBVear and then restore database from this dump.

For this operation - right click on the database name in left part of window and select Instruments->Restore.

All the new features are working:

    - upload, download, sorting files. files stored in blob fields of PostgresDB
    - tags added to Notes
    - news feed from AIOHTTP project integrated to bot
    - data connected to users, all users have separate scope of contacts and notes
    - tested the ability to working 2 users at one time (from 2 separate browsers on my laptop)

All test data dumped from database. You could do docker compose with .yaml file enclosed, than restore database from dump using DBVear.

