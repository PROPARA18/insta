from flask import Flask, render_template, request, redirect, session
from supabase import create_client

app = Flask(__name__)

# Secret key for Flask sessions
app.secret_key = "my-secret-key"


# ==============================
# SUPABASE
# ==============================

SUPABASE_URL = "https://glntbtbnvwljbptwfcsk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdsbnRidGJudndsamJwdHdmY3NrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkwMTU4NjAsImV4cCI6MjEwNDU5MTg2MH0.XJswbLy06UGNrIRA46t_YoRRJxEVIf-uIuKWX3ejO4E"


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ==============================
# LOGIN
# ==============================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # Search user in Supabase
        response = (
            supabase
            .table("users")
            .select("*")
            .eq("username", username)
            .eq("password", password)
            .execute()
        )

        if response.data:

            user = response.data[0]

            # Store logged-in user
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect("/profile")

        return "❌ Invalid username or password"

    return render_template("login.html")


# ==============================
# PROFILE
# ==============================

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/")

    response = (
        supabase
        .table("users")
        .select("*")
        .eq("id", session["user_id"])
        .execute()
    )

    user = response.data[0]

    return render_template(
        "profile.html",
        user=user
    )


# ==============================
# DM PAGE
# ==============================

@app.route("/dm/<int:user_id>")
def dm(user_id):

    if "user_id" not in session:
        return redirect("/")

    current_user = session["user_id"]

    # Get receiver
    receiver_response = (
        supabase
        .table("users")
        .select("*")
        .eq("id", user_id)
        .execute()
    )

    receiver = receiver_response.data[0]

    # Get messages between users
    response = (
        supabase
        .table("messages")
        .select("*")
        .or_(
            f"and(sender_id.eq.{current_user},receiver_id.eq.{user_id}),"
            f"and(sender_id.eq.{user_id},receiver_id.eq.{current_user})"
        )
        .order("created_at")
        .execute()
    )

    messages = response.data

    return render_template(
        "dm.html",
        receiver=receiver,
        messages=messages,
        current_user=current_user
    )


# ==============================
# SEND MESSAGE
# ==============================

@app.route("/send/<int:user_id>", methods=["POST"])
def send_message(user_id):

    if "user_id" not in session:
        return redirect("/")

    message = request.form["message"]

    supabase.table("messages").insert({
        "sender_id": session["user_id"],
        "receiver_id": user_id,
        "message": message
    }).execute()

    return redirect(f"/dm/{user_id}")


# ==============================
# LOGOUT
# ==============================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ==============================
# START SERVER
# ==============================

if __name__ == "__main__":

    print("\n================================")
    print("     📸 Instagram DM Demo")
    print("================================")
    print("🌐 http://127.0.0.1:5000/")
    print("🌐 http://localhost:5000/")
    print("================================\n")

    app.run(
        host="127.0.0.1",
        port=5002,
        debug=True
    )