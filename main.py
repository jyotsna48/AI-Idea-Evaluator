from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai
import os
import time

app = FastAPI(title="AI Idea Evaluator")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is missing.")

client = genai.Client(api_key=api_key)

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
Choose Easy, Medium, or Hard and explain why.

## 💡 Uniqueness
Give a score from 1 to 10 and explain it.

## 🛠️ Recommended Technologies
Suggest suitable technologies.

## 🚀 Improvements
Give exactly 3 practical improvements.

## 🏆 Final Verdict
Choose:
Highly Recommended / Recommended / Needs Improvement / Not Recommended

Be honest and practical.
"""

class IdeaRequest(BaseModel):
    idea: str

def evaluate_idea(idea):
    prompt = f"""
{SYSTEM_INSTRUCTION}

Evaluate this project idea:

{idea}
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            return response.text
        except Exception:
            if attempt < 2:
                time.sleep(5)
            else:
                return "Gemini is temporarily unavailable. Please try again later."

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>AI Idea Evaluator</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            margin: 0;
            padding: 40px 20px;
            color: #222;
        }
        .container {
            max-width: 850px;
            margin: auto;
            background: white;
            padding: 35px;
            border-radius: 18px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        }
        h1 {
            text-align: center;
            margin-bottom: 8px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 28px;
        }
        textarea {
            width: 100%;
            min-height: 130px;
            padding: 15px;
            border: 1px solid #ccc;
            border-radius: 10px;
            font-size: 16px;
            box-sizing: border-box;
            resize: vertical;
        }
        button {
            display: block;
            width: 100%;
            margin-top: 15px;
            padding: 14px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            background: #111827;
            color: white;
        }
        button:disabled {
            opacity: 0.6;
            cursor: wait;
        }
        #result {
            margin-top: 25px;
            padding: 20px;
            background: #f8fafc;
            border-radius: 12px;
            white-space: pre-wrap;
            line-height: 1.6;
            display: none;
        }
        .loading {
            text-align: center;
            color: #666;
        }
        .error {
            color: #b91c1c;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💡 AI Idea Evaluator</h1>
        <p class="subtitle">
            Enter your project idea and get an AI-powered evaluation.
        </p>

        <textarea id="idea" placeholder="Example: An AI app that helps college students find internships"></textarea>

        <button id="evaluateBtn" onclick="evaluateIdea()">
            🚀 Evaluate My Idea
        </button>

        <div id="result"></div>
    </div>

    <script>
        async function evaluateIdea() {
            const idea = document.getElementById("idea").value.trim();
            const button = document.getElementById("evaluateBtn");
            const result = document.getElementById("result");

            if (!idea) {
                alert("Please enter a project idea.");
                return;
            }

            button.disabled = true;
            button.textContent = "🤖 Evaluating...";
            result.style.display = "block";
            result.className = "";
            result.textContent = "Analyzing your idea...";

            try {
                const response = await fetch("/evaluate", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ idea: idea })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || "Something went wrong.");
                }

                result.textContent = data.evaluation;
            } catch (error) {
                result.className = "error";
                result.textContent = "❌ " + error.message;
            } finally {
                button.disabled = false;
                button.textContent = "🚀 Evaluate My Idea";
            }
        }
    </script>
</body>
</html>
"""

@app.post("/evaluate")
def evaluate(request: IdeaRequest):
    if not request.idea.strip():
        return {"idea": request.idea, "evaluation": "Please enter a project idea."}

    result = evaluate_idea(request.idea)

    return {
        "idea": request.idea,
        "evaluation": result
    }
