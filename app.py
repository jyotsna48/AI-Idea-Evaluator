
import os
import json

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai


app = FastAPI(
    title="UK Right AI Project Evaluator"
)


API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is missing."
    )


client = genai.Client(
    api_key=API_KEY
)


EVALUATION_CRITERIA = {
    "Problem Relevance": 20,
    "Innovation": 15,
    "Technical Feasibility": 15,
    "Social Impact": 15,
    "Scalability": 10,
    "AI Usage": 10,
    "User Experience": 5,
    "Security & Privacy": 5,
    "Implementation": 5
}


class ProjectRequest(BaseModel):

    project_name: str

    description: str

    technologies: str = ""

    target_users: str = ""


@app.get("/")
def home():

    return FileResponse(
        "static/index.html"
    )


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/evaluate")
def evaluate_project(project: ProjectRequest):

    criteria_text = "\n".join(
        f"- {criterion}: {weight}%"
        for criterion, weight
        in EVALUATION_CRITERIA.items()
    )


    prompt = f"""
You are an expert AI project evaluator.

Evaluate this project objectively.

PROJECT NAME:
{project.project_name}

DESCRIPTION:
{project.description}

TECHNOLOGIES:
{project.technologies}

TARGET USERS:
{project.target_users}

EVALUATION CRITERIA:
{criteria_text}

For every criterion:

Give a score from 0 to 100.

Explain the score briefly.

Calculate the weighted overall score.

Also provide:

- Overall rating
- Top 3 strengths
- Top 3 weaknesses
- Major risks
- Improvement recommendations
- Implementation recommendation
- Final evaluator summary

Return ONLY valid JSON.

Use this structure:

{{
    "project_name": "{project.project_name}",

    "scores": {{
        "Problem Relevance": 0,
        "Innovation": 0,
        "Technical Feasibility": 0,
        "Social Impact": 0,
        "Scalability": 0,
        "AI Usage": 0,
        "User Experience": 0,
        "Security & Privacy": 0,
        "Implementation": 0
    }},

    "explanations": {{
        "Problem Relevance": "",
        "Innovation": "",
        "Technical Feasibility": "",
        "Social Impact": "",
        "Scalability": "",
        "AI Usage": "",
        "User Experience": "",
        "Security & Privacy": "",
        "Implementation": ""
    }},

    "overall_score": 0,

    "rating": "",

    "strengths": [],

    "weaknesses": [],

    "risks": [],

    "recommendations": [],

    "implementation_recommended": true,

    "summary": ""
}}
"""


    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )


        text = response.text.strip()


        if text.startswith("```"):

            text = text.replace(
                "```json",
                ""
            )

            text = text.replace(
                "```",
                ""
            )

            text = text.strip()


        result = json.loads(text)

        return result


    except Exception as e:

        return {
            "error": str(e)
        }


app.mount(
    "/static",
    StaticFiles(
        directory="static"
    ),
    name="static"
)
