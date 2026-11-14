"""
app.py - Flask website for the Student Management Portal.

Run:  python app.py   then open http://127.0.0.1:5000
Default login: admin / admin123
"""

import csv
import io
import os
from functools import wraps

from flask import (Flask, Response, flash, redirect, render_template, request,
                   session, url_for)

import backend

app = Flask(__name__)
app.secret_key = os.environ.get("PORTAL_SECRET", "dev-secret-change-me")


def login_required(view):
    """Redirect anonymous visitors to the login page."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def flash_all(messages, category):
    for message in messages:
        flash(message, category)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = backend.user_login(request.form.get("username", ""),
                                  request.form.get("password", ""))
        if user:
            session["user"] = user["username"]
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", report=backend.generate_report())


@app.route("/students")
@login_required
def students():
    query = request.args.get("q", "")
    field = request.args.get("field", "name")
    records = backend.search_record(query, field)
    return render_template("students.html", records=records, query=query,
                           field=field, fields=backend.SEARCH_FIELDS)


@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        ok, messages = backend.add_record(request.form)
        if ok:
            flash_all(messages, "success")
            return redirect(url_for("students"))
        flash_all(messages, "error")
    return render_template("form.html", record=request.form, editing=False,
                           departments=backend.DEPARTMENTS)


@app.route("/students/<roll_no>/edit", methods=["GET", "POST"])
@login_required
def edit_student(roll_no):
    record = backend.find_record(roll_no)
    if record is None:
        flash("Student not found.", "error")
        return redirect(url_for("students"))
    if request.method == "POST":
        ok, messages = backend.update_record(roll_no, request.form)
        if ok:
            flash_all(messages, "success")
            return redirect(url_for("students"))
        flash_all(messages, "error")
        record = request.form.to_dict()
        record["roll_no"] = roll_no
    return render_template("form.html", record=record, editing=True,
                           departments=backend.DEPARTMENTS)


@app.route("/students/<roll_no>/delete", methods=["POST"])
@login_required
def delete_student(roll_no):
    ok, messages = backend.delete_record(roll_no)
    flash_all(messages, "success" if ok else "error")
    return redirect(url_for("students"))


@app.route("/report")
@login_required
def report():
    return render_template("report.html", report=backend.generate_report())


@app.route("/export.csv")
@login_required
def export_csv():
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Roll No", "Name", "Department", "Semester", "Marks", "Grade"])
    for r in backend.load_records():
        writer.writerow([r["roll_no"], r["name"], r["department"],
                         r["semester"], r["marks"], r["grade"]])
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=students.csv"})


if __name__ == "__main__":
    backend.load_users()  # make sure the default admin exists
    app.run(debug=True)
