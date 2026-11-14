# Student Management Portal

Assignment 3 — End-to-End Portal Design (Python). Team: **25L-5308 · 25L-5291**

A student record portal with a Python backend (JSON file storage) and a Flask website.
A terminal menu version is also included.

## Features
- Login with salted-hash passwords (`user_login`)
- Add, search, update and delete student records (`add_record`, `search_record`, `update_record`, `delete_record`)
- Performance report: averages, pass rate, grade distribution, department averages (`generate_report`)
- CSV export of all records
- Persistent storage in `data/students.json` and `data/users.json`
- Input validation and graceful error handling (`ValueError`, `FileNotFoundError`, `PermissionError`, corrupted JSON)

## Project structure
| File | Purpose |
|---|---|
| `backend.py` | Core logic: functions, file handling, error handling, terminal menu (`while True`) |
| `app.py` | Flask website (routes) that calls the backend |
| `templates/`, `static/` | HTML templates and CSS |
| `seed_data.py` | Loads 12 sample students |
| `Student_Portal.ipynb` | Runnable notebook with sample test runs |
| `data/` | Sample data files created by the portal |

## Run it
```bash
pip install -r requirements.txt
python seed_data.py      # optional: sample data
python app.py            # website at http://127.0.0.1:5000
python backend.py        # or: terminal menu
```
Default login: `admin` / `admin123`

## Error handling
- Missing data file → portal starts with an empty list
- Corrupted JSON → warning printed, portal starts empty instead of crashing
- No write permission → error reported, `False` returned
- Non-numeric / out-of-range marks and semester → validation messages shown to the user
- Duplicate roll numbers are rejected
