from flask import Flask, render_template, request
import re

app = Flask(__name__)

COMMON_PASSWORDS = {
    "password", "password123", "123456", "123456789", "qwerty",
    "admin", "letmein", "welcome", "iloveyou", "abc123"
}


def assess_password(password: str) -> dict:
    """Return a simple educational password-strength assessment."""
    checks = [
        ("At least 12 characters", len(password) >= 12),
        ("Contains lowercase letters", bool(re.search(r"[a-z]", password))),
        ("Contains uppercase letters", bool(re.search(r"[A-Z]", password))),
        ("Contains numbers", bool(re.search(r"\d", password))),
        ("Contains symbols", bool(re.search(r"[^A-Za-z0-9]", password))),
    ]
    score = sum(passed for _, passed in checks)
    if password.lower() in COMMON_PASSWORDS:
        score = min(score, 1)

    if len(password) < 8 or password.lower() in COMMON_PASSWORDS:
        label = "Weak"
    elif score <= 2:
        label = "Fair"
    elif score <= 4:
        label = "Good"
    else:
        label = "Strong"

    feedback = [
        f"Consider adding: {name.lower()}."
        for name, passed in checks if not passed
    ]
    if password.lower() in COMMON_PASSWORDS:
        feedback.append("Avoid common and predictable passwords.")
    if not feedback:
        feedback.append("Avoid reusing this password on other websites.")

    return {"score": score, "label": label, "checks": checks, "feedback": feedback}


@app.get("/")
def home():
    return render_template("index.html", result=None)


@app.post("/check")
def check():
    result = assess_password(request.form.get("password", ""))
    return render_template("index.html", result=result)


@app.get("/about")
def about():
    return render_template("about.html")


@app.get("/tips")
def tips():
    return render_template("tips.html")


@app.get("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    # Local Windows development port. Docker uses Gunicorn on port 5004.
    app.run(host="0.0.0.0", port=5002, debug=False)
