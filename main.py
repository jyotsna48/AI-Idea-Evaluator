
from fastapi import FastAPI
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


@app.get("/")
def home():
    return {
        "message": "AI Idea Evaluator is running!",
        "usage": "Send a POST request to /evaluate"
    }


@app.post("/evaluate")
def evaluate(request: IdeaRequest):

    result = evaluate_idea(request.idea)

    return {
        "idea": request.idea,
        "evaluation": result
    }
