from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai
import os
import time

app = FastAPI(title="AI Idea Evaluator")

# Get Gemini API key from Render Environment Variables
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is missing.")

client = genai.Client(api_key=api_key)


# =========================
# AI AGENT INSTRUCTIONS
# =========================

SYSTEM_INSTRUCTION = """
You are an AI Project Idea Evaluator.

Evaluate software, AI, and technology project ideas.

For every idea, provide:

## 💡 Project Idea
Briefly restate the idea.

## ⭐ Overall Score
Give a score from 1 to 10 and explain it briefly.

## 🎯 Problem
What real problem does this project solve?

## ✅ Strengths
Give exactly 3 strengths.

## ⚠️ Weaknesses
Give exactly 3 weaknesses.

## 📊 Difficulty
Choose one:
Easy / Medium / Hard

Explain why.

## 💡 Uniqueness
Give a score from 1 to 10.
Explain whether similar solutions are likely to exist.

## 🛠️ Recommended Technologies
Suggest suitable technologies for a college-level implementation.

## 🚀 Improvements
Give exactly 3 practical improvements.

## 🏆 Final Verdict
Choose one:

Highly Recommended
Recommended
Needs Improvement
Not Recommended

Explain your decision briefly.

Be honest and practical.
Do not give high scores just to make the user happy.
Keep the project realistic for a college student.
"""


# =========================
# REQUEST MODEL
# =========================

class IdeaRequest(BaseModel):
    idea: str


# =========================
# AI EVALUATION FUNCTION
# =========================

def evaluate_idea(idea):

    prompt = f"""
{SYSTEM_INSTRUCTION}

Evaluate this project idea:

{idea}
"""

    # Try multiple models if one is temporarily unavailable
    models = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite"
    ]

    for model in models:

        for attempt in range(2):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response.text:
                    return response.text

            except Exception as e:

                print(
                    f"Model {model} failed "
                    f"(attempt {attempt + 1}): {e}"
                )

                if attempt < 1:
                    time.sleep(3)

    return (
        "❌ Gemini is temporarily unavailable. "
        "Please try again in a few minutes."
    )


# =========================
# HOME PAGE
# =========================

@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>

<html>

<head>

    <title>AI Idea Evaluator</title>

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <style>

        * {
            box-sizing: border-box;
        }

        body {

            font-family: Arial, sans-serif;

            background:
                linear-gradient(
                    135deg,
                    #eef2ff,
                    #f8fafc
                );

            margin: 0;

            padding: 40px 20px;

            color: #222;
        }


        .container {

            max-width: 850px;

            margin: auto;

            background: white;

            padding: 35px;

            border-radius: 20px;

            box-shadow:
                0 10px 35px
                rgba(0,0,0,0.10);
        }


        h1 {

            text-align: center;

            margin-bottom: 8px;

            font-size: 34px;
        }


        .subtitle {

            text-align: center;

            color: #666;

            margin-bottom: 28px;

            font-size: 17px;
        }


        textarea {

            width: 100%;

            min-height: 150px;

            padding: 16px;

            border:
                1px solid #d1d5db;

            border-radius: 12px;

            font-size: 16px;

            resize: vertical;

            outline: none;
        }


        textarea:focus {

            border-color: #6366f1;

            box-shadow:
                0 0 0 3px
                rgba(99,102,241,0.12);
        }


        button {

            display: block;

            width: 100%;

            margin-top: 16px;

            padding: 15px;

            border: none;

            border-radius: 12px;

            font-size: 17px;

            font-weight: bold;

            cursor: pointer;

            background: #111827;

            color: white;

            transition: 0.2s;
        }


        button:hover {

            background: #374151;
        }


        button:disabled {

            opacity: 0.6;

            cursor: wait;
        }


        #result {

            margin-top: 25px;

            padding: 22px;

            background: #f8fafc;

            border-radius: 14px;

            white-space: pre-wrap;

            line-height: 1.7;

            display: none;

            border:
                1px solid #e5e7eb;
        }


        .error {

            color: #b91c1c;

            background: #fef2f2 !important;

            border-color: #fecaca !important;
        }


        .loading {

            text-align: center;

            color: #666;
        }


        .footer {

            text-align: center;

            margin-top: 20px;

            color: #888;

            font-size: 13px;
        }

    </style>

</head>


<body>


<div class="container">


    <h1>
        💡 AI Idea Evaluator
    </h1>


    <p class="subtitle">

        Enter your project idea and get
        an AI-powered evaluation.

    </p>


    <textarea
        id="idea"
        placeholder="Example: An AI app that helps college students find internships"
    ></textarea>


    <button
        id="evaluateBtn"
        onclick="evaluateIdea()"
    >

        🚀 Evaluate My Idea

    </button>


    <div id="result"></div>


    <div class="footer">

        Powered by Gemini AI

    </div>


</div>


<script>


async function evaluateIdea() {


    const idea =
        document
        .getElementById("idea")
        .value
        .trim();


    const button =
        document
        .getElementById("evaluateBtn");


    const result =
        document
        .getElementById("result");


    if (!idea) {

        alert(
            "Please enter a project idea."
        );

        return;
    }


    button.disabled = true;

    button.textContent =
        "🤖 Evaluating...";


    result.style.display =
        "block";


    result.className =
        "loading";


    result.textContent =
        "Analyzing your idea...";


    try {


        const response =
            await fetch(
                "/evaluate",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        idea: idea
                    })

                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Something went wrong."
            );

        }


        result.className = "";

        result.textContent =
            data.evaluation;


    }

    catch (error) {

        result.className =
            "error";

        result.textContent =
            "❌ " +
            error.message;

    }

    finally {

        button.disabled = false;

        button.textContent =
            "🚀 Evaluate My Idea";

    }

}


</script>


</body>

</html>
"""


# =========================
# EVALUATE API
# =========================

@app.post("/evaluate")
def evaluate(request: IdeaRequest):

    idea = request.idea.strip()


    if not idea:

        return {

            "idea": request.idea,

            "evaluation":
                "Please enter a project idea."

        }


    result =
        evaluate_idea(idea)


    return {

        "idea": idea,

        "evaluation": result

    }
