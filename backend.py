"""
backend.py - Student Management Portal (core logic)

Pure-Python backend used by both the web frontend (app.py) and the
terminal menu (run this file directly: python backend.py).

Concepts covered: functions (def), loops (for / while), file handling
(JSON persistence), and exception handling (try / except / finally).
"""

import hashlib
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

DEPARTMENTS = ["Computer Science", "Software Engineering", "Electrical Engineering",
               "Business Administration", "Law"]
SEARCH_FIELDS = ["name", "roll_no", "department"]


# --------------------------------------------------------------------------
# File handling helpers
# --------------------------------------------------------------------------
def load_json(path, default):
    """Read a JSON file and return its content.

    Returns `default` if the file is missing, empty or corrupted, so the
    portal never crashes on startup.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        print(f"[warning] {os.path.basename(path)} is corrupted; starting empty.")
        return default
    except PermissionError:
        print(f"[error] No permission to read {path}.")
        return default


def save_json(path, data):
    """Write `data` to a JSON file. Returns True on success, False on failure."""
    f = None
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        f = open(path, "w", encoding="utf-8")
        json.dump(data, f, indent=2)
        return True
    except PermissionError:
        print(f"[error] No permission to write {path}.")
        return False
    except OSError as exc:
        print(f"[error] Could not save {path}: {exc}")
        return False
    finally:
        if f is not None:
            f.close()


# --------------------------------------------------------------------------
# Users and login
# --------------------------------------------------------------------------
def hash_password(password, salt):
    """Return a salted SHA-256 hash of the password."""
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def load_users():
    """Load users, creating a default admin account on first run."""
    users = load_json(USERS_FILE, None)
    if not users:
        salt = os.urandom(8).hex()
        users = [{"username": "admin", "salt": salt,
                  "password_hash": hash_password("admin123", salt),
                  "role": "admin"}]
        save_json(USERS_FILE, users)
    return users


def user_login(username, password):
    """Check credentials. Returns the user dict (without secrets) or None."""
    for user in load_users():
        if user["username"] == username.strip():
            if hash_password(password, user["salt"]) == user["password_hash"]:
                return {"username": user["username"], "role": user["role"]}
            return None
    return None


# --------------------------------------------------------------------------
# Student records
# --------------------------------------------------------------------------
def load_records():
    """Return the list of all student records from disk."""
    records = load_json(STUDENTS_FILE, [])
    return records if isinstance(records, list) else []


def save_records(records):
    """Persist the list of student records."""
    return save_json(STUDENTS_FILE, records)


def get_grade(marks):
    """Convert a numeric mark (0-100) into a letter grade."""
    if marks >= 85:
        return "A"
    if marks >= 70:
        return "B"
    if marks >= 55:
        return "C"
    if marks >= 40:
        return "D"
    return "F"


def validate_record(data):
    """Validate raw form/console input.

    Returns (clean_record, errors). `errors` is a list of messages; the
    record is only usable when it is empty.
    """
    errors = []
    name = str(data.get("name", "")).strip()
    roll_no = str(data.get("roll_no", "")).strip().upper()
    department = str(data.get("department", "")).strip()

    if not name:
        errors.append("Name is required.")
    if not roll_no:
        errors.append("Roll number is required.")
    if not department:
        errors.append("Department is required.")

    try:
        semester = int(data.get("semester"))
        if not 1 <= semester <= 8:
            errors.append("Semester must be between 1 and 8.")
    except (TypeError, ValueError):
        semester = None
        errors.append("Semester must be a whole number.")

    try:
        marks = float(data.get("marks"))
        if not 0 <= marks <= 100:
            errors.append("Marks must be between 0 and 100.")
    except (TypeError, ValueError):
        marks = None
        errors.append("Marks must be a number.")

    clean = {"roll_no": roll_no, "name": name, "department": department,
             "semester": semester, "marks": marks}
    if marks is not None:
        clean["grade"] = get_grade(marks)
    return clean, errors


def find_record(roll_no):
    """Return the record with this roll number, or None."""
    roll_no = str(roll_no).strip().upper()
    for record in load_records():
        if record["roll_no"] == roll_no:
            return record
    return None


def add_record(data):
    """Add a new student. Returns (success, message_or_errors)."""
    clean, errors = validate_record(data)
    if errors:
        return False, errors
    records = load_records()
    for record in records:
        if record["roll_no"] == clean["roll_no"]:
            return False, [f"Roll number {clean['roll_no']} already exists."]
    records.append(clean)
    if not save_records(records):
        return False, ["Could not save to disk."]
    return True, [f"Added {clean['name']} ({clean['roll_no']})."]


def update_record(roll_no, data):
    """Update an existing student. Returns (success, message_or_errors)."""
    roll_no = str(roll_no).strip().upper()
    data = dict(data, roll_no=roll_no)  # roll number cannot be changed
    clean, errors = validate_record(data)
    if errors:
        return False, errors
    records = load_records()
    for i, record in enumerate(records):
        if record["roll_no"] == roll_no:
            records[i] = clean
            if not save_records(records):
                return False, ["Could not save to disk."]
            return True, [f"Updated {clean['name']}."]
    return False, [f"No student with roll number {roll_no}."]


def delete_record(roll_no):
    """Delete a student. Returns (success, message)."""
    roll_no = str(roll_no).strip().upper()
    records = load_records()
    remaining = [r for r in records if r["roll_no"] != roll_no]
    if len(remaining) == len(records):
        return False, [f"No student with roll number {roll_no}."]
    if not save_records(remaining):
        return False, ["Could not save to disk."]
    return True, [f"Deleted {roll_no}."]


def search_record(query="", field="name"):
    """Return records whose `field` contains `query` (case-insensitive).

    An empty query returns every record.
    """
    if field not in SEARCH_FIELDS:
        field = "name"
    query = str(query).strip().lower()
    results = []
    for record in load_records():
        if query in str(record.get(field, "")).lower():
            results.append(record)
    return results


def generate_report():
    """Build summary statistics for the dashboard and report page."""
    records = load_records()
    report = {"total": len(records), "average": 0.0, "highest": None,
              "lowest": None, "grades": {g: 0 for g in "ABCDF"},
              "by_department": {}, "pass_rate": 0.0}
    if not records:
        return report

    total_marks = 0.0
    passed = 0
    for record in records:
        marks = record["marks"]
        total_marks += marks
        report["grades"][get_grade(marks)] += 1
        if marks >= 40:
            passed += 1
        dept = report["by_department"].setdefault(
            record["department"], {"count": 0, "total": 0.0})
        dept["count"] += 1
        dept["total"] += marks

    for dept in report["by_department"].values():
        dept["average"] = round(dept["total"] / dept["count"], 1)

    report["average"] = round(total_marks / len(records), 1)
    report["highest"] = max(records, key=lambda r: r["marks"])
    report["lowest"] = min(records, key=lambda r: r["marks"])
    report["pass_rate"] = round(passed / len(records) * 100, 1)
    return report


# --------------------------------------------------------------------------
# Terminal menu (optional way to use the portal without the website)
# --------------------------------------------------------------------------
def _print_records(records):
    if not records:
        print("  (no records)")
        return
    print(f"  {'Roll No':<12}{'Name':<24}{'Department':<24}{'Sem':<5}{'Marks':<7}Grade")
    for r in records:
        print(f"  {r['roll_no']:<12}{r['name']:<24}{r['department']:<24}"
              f"{r['semester']:<5}{r['marks']:<7}{r['grade']}")


def _ask_record():
    return {"name": input("Name: "), "roll_no": input("Roll no: "),
            "department": input("Department: "), "semester": input("Semester (1-8): "),
            "marks": input("Marks (0-100): ")}


def main():
    """Interactive console loop; runs until the user chooses Exit."""
    print("=== Student Management Portal ===")
    user = None
    for _ in range(3):
        user = user_login(input("Username: "), input("Password: "))
        if user:
            break
        print("Invalid credentials.")
    if not user:
        print("Too many failed attempts.")
        return

    while True:
        print("\n1) List  2) Add  3) Search  4) Update  5) Delete  6) Report  7) Exit")
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                _print_records(load_records())
            elif choice == "2":
                ok, msgs = add_record(_ask_record())
                print("\n".join(msgs))
            elif choice == "3":
                field = input(f"Search by {SEARCH_FIELDS}: ").strip() or "name"
                _print_records(search_record(input("Query: "), field))
            elif choice == "4":
                roll = input("Roll no to update: ")
                ok, msgs = update_record(roll, _ask_record())
                print("\n".join(msgs))
            elif choice == "5":
                ok, msgs = delete_record(input("Roll no to delete: "))
                print("\n".join(msgs))
            elif choice == "6":
                rep = generate_report()
                print(f"Students: {rep['total']}  Average: {rep['average']}  "
                      f"Pass rate: {rep['pass_rate']}%")
                for grade, count in rep["grades"].items():
                    print(f"  {grade}: {'#' * count} ({count})")
            elif choice == "7":
                print("Goodbye.")
                break
            else:
                print("Please choose 1-7.")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break


if __name__ == "__main__":
    main()
