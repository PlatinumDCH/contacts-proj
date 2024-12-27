добавить кусок пути до проекта в PYTHONPATH .env
пример:
    PYTHONPATH = /Users/plarium/Develop/cources/Python_web/contacts-proj
в фале можно импоритровать другие модули по абсолютному пути
- запускать такой файл можно  с корневого каталога проета


запуск сервера
uvicorn app.main:app --reload

работа с алембиком
cd project/root
alembic init <name folder>
alembic revision --autogenerate -m 'commit'
alembic upgrade head


====================================
ТУДУ:
    дописать тесты для  repo_user
    

====================================

проверить покрытие тестами 
 pytest --cov=app 

запуск воркера
cd /Users/plarium/Develop/cources/Python_web/contacts-proj
PYTHONPATH=. python app/services/rabbit_send/worker.py

запусе pytest
cd /Users/plarium/Develop/cources/Python_web/contacts-proj
PYTHONPATH=. pytest



Структура jwt service

JWTService
    SECRET_KEY
    ALGORITHM
    create_access_token
    create_refresh_token
    create_email_token
    create_re_pass_token
    decode_token
EmailService(JWTService)
    send_email
    pocess_email_confirmation
    process_email_change_pass
"""

фикстура - функции, которые создают окружение вокруг тестов


удалить файл из репозитория и добавить в гитигнор

echo "name file" >> .gitignore
git add .gitignore
git commit -m "Add name_file to .gitignore"

git rm --cached .coverage простое удаление папки-файла
git rm -r --cached .coverage рекурсивное удаление папки
git commit -m "Removed .coverage from repository"
git push
