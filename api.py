import os
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import Field

from experiments import run_experiment
from prompts import build_checklist_messages, build_judge_messages
from schemas import (
    Allergen,
    JudgeAssessment,
    RecipeAnalysis,
    StrictModel,
)


class AnalyseRequest(StrictModel):
    recipe_text: str = Field(min_length=10, max_length=12000)
    target_allergen: Allergen | None = None


class AnalyseResponse(StrictModel):
    analysis: RecipeAnalysis
    judge: JudgeAssessment | None
    judge_status: str


app = FastAPI(title="Vegetarian Recipe and Allergen Assistant")


@lru_cache(maxsize=1)
def get_llm_connection():
    """Load configuration once and reuse the client."""

    load_dotenv()

    required = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT",
    ]

    if any(not os.getenv(name, "").strip() for name in required):
        raise HTTPException(
            status_code=503,
            detail="Required LLM configuration is missing.",
        )

    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].strip().rstrip("/")

    client = OpenAI(
        base_url=f"{endpoint}/openai/v1/",
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        timeout=60,
        max_retries=0,
    )

    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"].strip()

    return client, deployment


@app.get("/health")
def health():
    # Process health only; this does not call or verify Azure.
    return {"status": "ok"}


@app.post("/analyse", response_model=AnalyseResponse)
def analyse(request: AnalyseRequest):
    client, deployment = get_llm_connection()
    recipe_input = request.model_dump()

    analysis_attempt = run_experiment(
        client=client,
        deployment=deployment,
        messages=build_checklist_messages(**recipe_input),
        output_model=RecipeAnalysis,
    )

    if analysis_attempt["status"] != "valid":
        raise HTTPException(
            status_code=502,
            detail="Recipe analysis could not be completed or validated.",
        )

    analysis = RecipeAnalysis.model_validate(
        analysis_attempt["validated_output"]
    )

    judge_attempt = run_experiment(
        client=client,
        deployment=deployment,
        messages=build_judge_messages(
            recipe_input=recipe_input,
            candidate=analysis.model_dump(),
        ),
        output_model=JudgeAssessment,
    )

    judge = None

    if judge_attempt["status"] == "valid":
        judge = JudgeAssessment.model_validate(
            judge_attempt["validated_output"]
        )

    return AnalyseResponse(
        analysis=analysis,
        judge=judge,
        judge_status=judge_attempt["status"],
    )