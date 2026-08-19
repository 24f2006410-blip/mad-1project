from flask import Flask, render_template, request,redirect,session
from config import Config
from models import db, User, Trek, Booking
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Create database and default admin
with app.app_context():
    db.create_all()

    admin = User.query.filter_by(role="admin").first()

    if admin is None:
        admin = User(
            name="Administrator",
            email="admin@gmail.com",
            password=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            if user.role == "admin":

                total_treks = Trek.query.count()
                total_users = User.query.filter_by(role="user").count()
                total_staff = User.query.filter_by(role="staff").count()
                total_bookings = Booking.query.count()

                return render_template(
                    "admin/dashboard.html",
                    total_treks=total_treks,
                    total_users=total_users,
                    total_staff=total_staff,
                    total_bookings=total_bookings

                )    
    
            elif user.role == "staff":
                treks = Trek.query.filter_by(staff_id=user.id).all()

                return render_template(
                    "staff/dashboard.html",
                    treks=treks
                )    

            else:
                return render_template("user/dashboard.html")

        return "Invalid Email or Password"

    return render_template("login.html")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]
        

        user = User(
            name=name,
            email=email,
            password=password,
            role=role,
            status="pending" if role == "staff" else "Active"
        )

        db.session.add(user)
        db.session.commit()

        return "Registration Successful"

    return render_template("register.html")


# Admin Routes

@app.route("/create_trek", methods=["GET", "POST"])
def create_trek():

    if request.method == "POST":

        trek = Trek(
            name=request.form["name"],
            location=request.form["location"],
            difficulty=request.form["difficulty"],
            duration=int(request.form["duration"]),
            slots=int(request.form["slots"]),
            status=request.form["status"],
            start_date=datetime.strptime(request.form["start_date"], "%Y-%m-%d").date(),
            end_date=datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
        )

        db.session.add(trek)
        db.session.commit()

        return "Trek Created Successfully"

    return render_template("create_trek.html")


@app.route("/view_treks")
def view_treks():

    search = request.args.get("search")
    location = request.args.get("location")
    difficulty = request.args.get("difficulty")

    treks = Trek.query

    if search:
        treks = treks.filter(Trek.name.like(f"%{search}%"))

    if location:
        treks = treks.filter(Trek.location.like(f"%{location}%"))

    if difficulty:
        treks = treks.filter(Trek.difficulty == difficulty)

    treks = treks.all()

    return render_template(
        "view_treks.html",
        treks=treks
    )


'''@app.route("/view_users")
def view_users():

    users = User.query.filter_by(role="user").all()

    data = ""

    for u in users:
        data += f"{u.id} - {u.name} - {u.email}<br>"

    return data'''


'''@app.route("/view_staff")
def view_staff():

    staff = User.query.filter_by(role="staff").all()

    data = ""

    for s in staff:
        data += f"{s.id} - {s.name} - {s.email}<br>"

    return data'''


'''@app.route("/approve_staff")
def approve_staff():
    return "Approve Staff Page"


@app.route("/view_bookings")
def view_bookings():
    return "View Bookings Page"'''

# Edit Trek
@app.route("/edit_trek/<int:id>", methods=["GET", "POST"])
def edit_trek(id):

    trek = Trek.query.get_or_404(id)

    if request.method == "POST":

        trek.name = request.form["name"]
        trek.location = request.form["location"]
        trek.difficulty = request.form["difficulty"]
        trek.duration = int(request.form["duration"])
        trek.slots = int(request.form["slots"])
        trek.status = request.form["status"]
        trek.start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        trek.end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()

        db.session.commit()

        return "Trek Updated Successfully"

    return render_template("edit_trek.html", trek=trek)


# Delete Trek
@app.route("/delete_trek/<int:id>")
def delete_trek(id):

    trek = Trek.query.get_or_404(id)

    db.session.delete(trek)
    db.session.commit()

    return redirect("/view_treks")

@app.route("/book_trek/<int:id>")
def book_trek(id):

    trek = Trek.query.get_or_404(id)

    if trek.status != "Open":
        return "Booking Not Allowed. Trek is Closed."

    if trek.slots <= 0:
        return "No Slots Available."

    booking = Booking(
        user_id=2,      # Abhi test ke liye
        trek_id=id
    )

    db.session.add(booking)

    trek.slots = trek.slots - 1

    db.session.commit()

    return "Trek Booked Successfully"

@app.route("/my_bookings")
def my_bookings():

    bookings = Booking.query.filter_by(user_id=2).all()

    return render_template("my_bookings.html", bookings=bookings)

@app.route("/view_bookings")
def view_bookings():

    bookings = Booking.query.all()

    return render_template("view_bookings.html", bookings=bookings)

@app.route("/view_users")
def view_users():

    users = User.query.filter_by(role="user").all()

    return render_template("view_users.html", users=users)

@app.route("/view_staff")
def view_staff():

    staff = User.query.filter_by(role="staff").all()

    return render_template("view_staff.html", staff=staff)

@app.route("/approve_staff/<int:id>")
def approve_staff(id):

    staff = User.query.get_or_404(id)

    staff.status = "Active"

    db.session.commit()

    return redirect("/view_staff")

@app.route("/assign_staff/<int:id>", methods=["GET", "POST"])
def assign_staff(id):

    trek = Trek.query.get_or_404(id)
    staff = User.query.filter_by(role="staff").all()

    if request.method == "POST":
        trek.staff_id = request.form["staff_id"]
        db.session.commit()
        return redirect("/view_treks")

    return render_template(
        "assign_staff.html",
        trek=trek,
        staff=staff
    )

@app.route("/blacklist_user/<int:id>")
def blacklist_user(id):

    user = User.query.get_or_404(id)

    user.status = "Blacklisted"

    db.session.commit()

    return redirect("/view_users")

@app.route("/blacklist_staff/<int:id>")
def blacklist_staff(id):

    staff = User.query.get_or_404(id)

    staff.status = "Blacklisted"

    db.session.commit()

    return redirect("/view_staff")

@app.route("/staff_edit_trek/<int:id>", methods=["GET", "POST"])
def staff_edit_trek(id):

    trek = Trek.query.get_or_404(id)

    if request.method == "POST":

        trek.slots = int(request.form["slots"])
        trek.status = request.form["status"]

        db.session.commit()

        return "Trek Updated Successfully"

    return render_template("staff_edit_trek.html", trek=trek)

@app.route("/participants/<int:trek_id>")
def participants(trek_id):

    bookings = Booking.query.filter_by(trek_id=trek_id).all()

    return render_template(
        "participants.html",
        bookings=bookings
    )

@app.route("/edit_profile/<int:id>", methods=["GET", "POST"])
def edit_profile(id):

    user = User.query.get_or_404(id)

    if request.method == "POST":

        user.name = request.form["name"]
        user.email = request.form["email"]

        db.session.commit()

        return "Profile Updated Successfully"

    return render_template("edit_profile.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
    
if __name__ == "__main__":
    app.run(debug=True)