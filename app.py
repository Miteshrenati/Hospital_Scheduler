from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS doctors(
            doctorId TEXT PRIMARY KEY,
            specialization TEXT,
            maxDailyPatients INTEGER,
            currentAppointments INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")


# ---------- ADD DOCTOR ----------
@app.route("/add", methods=["GET","POST"])
def add_doctor():
    if request.method == "POST":
        doctorId = request.form["doctorId"]
        specialization = request.form["specialization"]
        maxPatients = request.form["maxPatients"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO doctors VALUES (?,?,?,?)",
            (doctorId, specialization, maxPatients, 0)
        )

        conn.commit()
        conn.close()

        return redirect("/doctors")

    return render_template("add_doctor.html")


# ---------- DOCTORS LIST ----------
@app.route("/doctors")
def doctors():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM doctors")
    data = cur.fetchall()
    conn.close()

    return render_template("doctors.html", doctors=data)

@app.route("/book", methods=["GET","POST"])
def book():
    if request.method == "POST":
        specialization = request.form["specialization"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        # get doctors of that specialization
        cur.execute("SELECT * FROM doctors WHERE specialization=?", (specialization,))
        doctors = cur.fetchall()

        if not doctors:
            conn.close()
            return render_template("result.html", message="No doctor available")

        # filter available doctors
        available = [d for d in doctors if d[3] < d[2]]

        if not available:
            conn.close()
            return render_template("result.html", message="All doctors are full")

        # choose doctor with minimum appointments
        selected = min(available, key=lambda x: x[3])

        # update appointment count
        cur.execute(
            "UPDATE doctors SET currentAppointments = currentAppointments + 1 WHERE doctorId=?",
            (selected[0],)
        )

        conn.commit()
        conn.close()

        return render_template("result.html",
                               message=f"Appointment booked with Doctor {selected[0]}")

    return render_template("book.html")



# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
