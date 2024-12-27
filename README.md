# Project Setup Guide

## Environment Configuration

### Add Project Path to `PYTHONPATH`

Add the following line to your `.env` file to include the project path in `PYTHONPATH`:
```env
PYTHONPATH=/Users/plarium/Develop/cources/Python_web/contacts-proj
```
This allows importing other modules using absolute paths.

### Server Startup
Run the server using the following command:
```bash
uvicorn app.main:app --reload
```

## Alembic Workflow

1. **Initialize Alembic**:
   ```bash
   cd project/root
   alembic init <name_folder>
   ```

2. **Generate a New Revision**:
   ```bash
   alembic revision --autogenerate -m "commit"
   ```

3. **Apply Migrations**:
   ```bash
   alembic upgrade head
   ```

---

## TODO:
- Write additional tests for `repo_user`.

---

## Test Coverage
Check the test coverage using:
```bash
pytest --cov=app
```

## Worker Startup
Run the worker with:
```bash
cd /Users/plarium/Develop/cources/Python_web/contacts-proj
PYTHONPATH=. python app/services/rabbit_send/worker.py
```

## Run Tests
Execute tests with:
```bash
cd /Users/plarium/Develop/cources/Python_web/contacts-proj
PYTHONPATH=. pytest
```

---

## JWT Service Structure

### `JWTService`
- **Attributes**:
  - `SECRET_KEY`
  - `ALGORITHM`

- **Methods**:
  - `create_access_token`
  - `create_refresh_token`
  - `create_email_token`
  - `create_re_pass_token`
  - `decode_token`

### `EmailService` (inherits from `JWTService`)
- **Methods**:
  - `send_email`
  - `process_email_confirmation`
  - `process_email_change_pass`

---

## Notes on Fixtures
Fixtures are functions that set up the environment for tests.

---

## Remove a File from Repository and Add to `.gitignore`

1. Add the file to `.gitignore`:
   ```bash
   echo "<file_name>" >> .gitignore
   git add .gitignore
   git commit -m "Add <file_name> to .gitignore"
   ```

2. Remove the file from the repository:
   ```bash
   git rm --cached <file_name>        # For a single file
   git rm -r --cached <folder_name>   # For a folder
   git commit -m "Removed <file_name> from repository"
   git push
   ```

