добавить кусок пути до проекта в PYTHONPATH .env
пример:
    PYTHONPATH = /Users/plarium/Develop/cources/Python_web/contacts-proj
в фале можно импоритровать другие модули по абсолютному пути
- запускать такой файл можно  с корневого каталога проета


запуск сервера
uvicorn app.main:app --reload

cd project/root
alembic init <name folder>
alembic revision --autogenerate -m 'commit'
alembic upgrade head



ТУДУ:

