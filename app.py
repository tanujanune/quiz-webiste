from flask import Flask, render_template, request, redirect, url_for
import requests
import html
import random

app = Flask(__name__)

API_URL = "https://opentdb.com/api.php"

def get_questions(amount=5, difficulty="medium"):
    """Fetch questions dynamically from Open Trivia API"""
    params = {
        "amount": amount,
        "type": "multiple",   # multiple choice questions
        "difficulty": difficulty
    }
    response = requests.get(API_URL, params=params)
    data = response.json()

    questions = []
    for q in data["results"]:
        # mix correct + incorrect answers
        options = q["incorrect_answers"] + [q["correct_answer"]]
        random.shuffle(options)

        questions.append({
            "question": html.unescape(q["question"]),
            "options": [html.unescape(opt) for opt in options],
            "answer": html.unescape(q["correct_answer"])
        })
    return questions

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        score = 0
        for i, q in enumerate(app.config["QUESTIONS"]):
            selected = request.form.get(f"q{i}")
            if selected == q["answer"]:
                score += 1
        return redirect(url_for("result", score=score))

    # Fetch fresh random questions every time
    app.config["QUESTIONS"] = get_questions(amount=7, difficulty="easy")
    return render_template("quiz.html", questions=app.config["QUESTIONS"])

@app.route("/result")
def result():
    score = request.args.get("score")
    return render_template("result.html", score=score, total=len(app.config["QUESTIONS"]))

if __name__ == "__main__":
    app.run(debug=True)
