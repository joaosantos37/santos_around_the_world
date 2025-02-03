import os
import cursor
from cursor import render_template, request, redirect, url_for, flash, session
from models import db, User, Pin

app = cursor.App(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///family_map.db'
app.secret_key = os.urandom(24)

db.init_app(app)

@app.on_event("startup")
def startup():
    with app.app_context():
        db.create_all()
        # Pre-populate users if they do not exist
        if User.query.count() == 0:
            users = [
                {"username": "Maria", "color": "#FF0000"},
                {"username": "Saul", "color": "#00FF00"},
                {"username": "Tomás", "color": "#0000FF"},
                {"username": "Mario", "color": "#FFFF00"},
                {"username": "Elisabete", "color": "#FF00FF"},
                {"username": "Natalia", "color": "#00FFFF"}
            ]
            for u in users:
                user = User(username=u["username"], color=u["color"])
                db.session.add(user)
            db.session.commit()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        user = User.query.filter_by(username=username).first()
        if user:
            session["user_id"] = user.id
            flash("Logged in successfully")
            return redirect(url_for("world_map"))
        else:
            flash("User not found.")
    # Provide the list of users for selection in the login page.
    return render_template("login.html", users=User.query.all())

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out.")
    return redirect(url_for("index"))

@app.route("/map")
def world_map():
    # Retrieve all pins to display on the map.
    pins = Pin.query.all()
    return render_template("map.html", pins=pins)

@app.route("/pin", methods=["GET", "POST"])
def add_pin():
    if "user_id" not in session:
        flash("Please log in to add a pin.")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        country = request.form.get("country")
        pos = request.form.get("pos")
        cons = request.form.get("cons")
        description = request.form.get("description")
        # (Optional) You'll need to handle file uploads for images separately.
        image_paths = request.form.get("image_paths", None)
        
        new_pin = Pin(
            user_id=session["user_id"],
            country=country,
            pos=pos,
            cons=cons,
            description=description,
            image_paths=image_paths
        )
        db.session.add(new_pin)
        db.session.commit()
        flash("Pin added successfully")
        return redirect(url_for("world_map"))
    return render_template("pin_form.html")

if __name__ == "__main__":
    app.run(debug=True)





