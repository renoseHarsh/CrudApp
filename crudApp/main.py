import functools
import re

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import update
from werkzeug.security import check_password_hash, generate_password_hash

from .models import *
from .sqlalchemy import db

main = Blueprint("main", __name__)


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "" or password == "":
            return render_template("login.html", error="Need username and password")
        if (
            len(username) < 4
            or len(password) < 4
            or len(username) > 50
            or len(password) > 129
        ):
            return render_template(
                "login.html",
                error="Too Long/Short",
            )
        try:
            log_user = (
                db.session.execute(
                    db.select(User.id, User.password).where(User.username == username)
                )
                .mappings()
                .first()
            )
            if log_user:
                if check_password_hash(log_user.password, password):
                    session.clear()
                    session["user_id"] = log_user.id
                    return redirect(url_for("main.home"))
            return render_template("login.html", error="Invalid username or password")
        except Exception as e:
            print(e)
            return render_template("login.html", error="Database error")
    return render_template("login.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "" or password == "":
            return render_template("register.html", error="Need username and password")
        if (
            len(username) < 4
            or len(password) < 4
            or len(username) > 50
            or len(password) > 129
        ):
            return render_template(
                "register.html",
                error="Too Long/Short",
            )
        try:
            maybe_user = db.session.execute(
                db.select(User.id).where(User.username == username)
            ).first()
            if maybe_user is not None:
                return render_template("register.html", error="User already exists")
        except:
            return render_template("register.html", error="Database error")

        try:
            new_user = User(
                username=username,
                password=generate_password_hash(password),
            )
            db.session.add(new_user)
            db.session.commit()
        except:
            return render_template("register.html", error="Database error")
        session.clear()
        session["user_id"] = new_user.id
        return redirect(url_for("main.home"))
    return render_template("register.html")


@main.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" in session:
            try:
                g.user = db.session.execute(
                    db.select(User).where(User.id == session["user_id"])
                ).scalar_one_or_none()
                if g.user:
                    return view(**kwargs)
            except Exception as e:
                print(e)

        return redirect(url_for("main.login"))

    return wrapped_view


@main.route("/")
@login_required
def home():
    employees = (
        db.session.execute(db.select(Employee).where(Employee.UserID == g.user.id))
        .scalars()
        .all()
    )
    return render_template("home.html", username=g.user.username, employees=employees)


@main.route("/create-employee", methods=["GET", "POST"])
@login_required
def create_employee():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        if not name or not email:
            return render_template("create.html", error="Name and email are required")
        if len(name) < 3 or len(name) > 100 or len(email) > 100 or len(email) < 5:
            return render_template("create.html", error="Name or email too long")
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, email):
            return render_template("create.html", error="Invalid email format")

        try:
            maybe_emp = db.session.execute(
                db.select(Employee.EmployeeID).where(Employee.Email == email)
            ).first()
            if maybe_emp is not None:
                return render_template("create.html", error="Email already exists")
        except Exception as e:
            print(e)
            return render_template("create.html", error="Database error")

        department = request.form["department"]
        salary = request.form["salary"]
        joiningData = request.form["joiningDate"]

        try:
            new_employee = Employee(
                Name=name,
                Email=email,
                Department=department,
                Salary=salary,
                JoiningDate=joiningData,
                UserID=g.user.id,
            )
            db.session.add(new_employee)
            db.session.commit()
            return redirect(url_for("main.home"))
        except Exception as e:
            print(e)
            return render_template("create.html", error="Database error")

    return render_template("create.html")


@main.route("/delete-employee/<int:employee_id>")
@login_required
def delete_employee(employee_id):
    try:
        employee = db.session.execute(
            db.select(Employee).where(Employee.EmployeeID == employee_id)
        ).scalar_one_or_none()
        if employee and employee.UserID == g.user.id:
            db.session.delete(employee)
            db.session.commit()
            return redirect(url_for("main.home"))
        else:
            flash("You do not have permission to delete this employee.")
            return render_template("home.html")

    except Exception as e:
        print(e)
    return False


@main.route("/update-employee/<int:employee_id>", methods=["GET", "POST"])
@login_required
def update_employee(employee_id):
    if request.method == "GET":
        employee = (
            db.session.execute(
                db.select(Employee).where(
                    Employee.EmployeeID == employee_id, Employee.UserID == g.user.id
                )
            )
            .scalars()
            .first()
        )
        if not employee:
            flash("You do not have permission to edit this employee.")
            return redirect(url_for("main.home"))
        return render_template("create.html", employee=employee, edit=True)

    department = request.form["department"]
    salary = request.form["salary"]

    db.session.execute(
        update(Employee)
        .values(
            Department=department,
            Salary=salary,
        )
        .where(Employee.EmployeeID == employee_id)
    )
    db.session.commit()
    return redirect(url_for("main.home"))
