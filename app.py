
from flask import Flask, render_template, request
import re

app = Flask(__name__)


def cfg_check(password):
    """CFG: S -> SS | (S) | [S] | {S} | other characters.
    A stack checks balanced brackets in the password.
    """
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}

    for char in password:
        if char in "([{":
            stack.append(char)
        elif char in ")]}":
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()

    return len(stack) == 0


def analyze_password(password):
    checks = {
        "At least 8 characters": len(password) >= 8,
        "Uppercase letter": bool(re.search(r"[A-Z]", password)),
        "Lowercase letter": bool(re.search(r"[a-z]", password)),
        "Digit": bool(re.search(r"\d", password)),
        "Special character": bool(
            re.search(r"[^A-Za-z0-9]", password)
        ),
        "At least 12 characters": len(password) >= 12
    }

    score = sum(checks.values())
    suggestions = []

    if len(password) < 8:
        suggestions.append("Use at least 8 characters.")
    if not checks["Uppercase letter"]:
        suggestions.append("Add an uppercase letter.")
    if not checks["Lowercase letter"]:
        suggestions.append("Add a lowercase letter.")
    if not checks["Digit"]:
        suggestions.append("Add a number.")
    if not checks["Special character"]:
        suggestions.append("Add a special character.")
    if len(password) < 12:
        suggestions.append("Consider using 12 or more characters.")

    if re.search(r"(.)\1{2,}", password):
        suggestions.append("Avoid repeating the same character.")
        score -= 1

    if re.search(r"1234|abcd|qwerty|password", password, re.I):
        suggestions.append("Avoid common words and sequences.")
        score -= 1

    # Finite-state style validation: all required rules must pass.
    fa_accepted = all([
        len(password) >= 8,
        checks["Uppercase letter"],
        checks["Lowercase letter"],
        checks["Digit"],
        checks["Special character"]
    ])

    # CFG structural check: balanced (), [] and {}.
    cfg_accepted = cfg_check(password)

    if not cfg_accepted:
        suggestions.append("Check that brackets (), [] and {} are balanced.")

    if score >= 6 and fa_accepted and cfg_accepted:
        strength = "Strong"
    elif score >= 4 and cfg_accepted:
        strength = "Medium"
    else:
        strength = "Weak"

    if not suggestions:
        suggestions.append("Good! Continue using unique passwords.")

    return {
        "checks": checks,
        "strength": strength,
        "score": max(0, score),
        "fa_accepted": fa_accepted,
        "cfg_accepted": cfg_accepted,
        "suggestions": suggestions
    }


@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        password = request.form.get("password", "")
        result = analyze_password(password)

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
    