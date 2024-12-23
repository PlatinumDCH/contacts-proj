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


project/
    __init__.py
    src/
        model.py
    tests/
        testmodel.py

 
get http://127.0.0.1:8000/api/contacts/all 
post http://127.0.0.1:8000/api/contacts 
get http://127.0.0.1:8000/api/contacts/{contacts-id} 
put http://127.0.0.1:8000/api/contacts/{contacts-id}
delete http://127.0.0.1:8000/api/contacts/5