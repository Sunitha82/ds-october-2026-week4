import json
import os
from pathlib import Path
from typing import get_args

import httpx
import streamlit as st
from pydantic import ValidationError

from schemas import Allergen, JudgeAssessment, RecipeAnalysis


st.set_page_config(
    page_title="Vegetarian Recipe Assistant",
    page_icon="🌿",
    layout="wide",
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
PROJECT_DIR = Path(__file__).resolve().parent

DEMO_PATH = (
    PROJECT_DIR / "data" / "vegetarian_recipe_dataset_v1" / "demo.json"
)


def clear_results():
    """Prevent old results being displayed for changed inputs."""
    st.session_state.pop("last_response", None)


def use_example(example):
    """Fill the input without making an API request."""
    st.session_state["recipe_text"] = example["input"]["recipe_text"]
    st.session_state["target_allergen"] = example["input"]["target_allergen"]
    clear_results()


def readable(value):
    return value.replace("_", " ").capitalize()


def allergen_list(values):
    return ", ".join(readable(value) for value in values) or "None identified"


st.session_state.setdefault("recipe_text", "")
st.session_state.setdefault("target_allergen", None)

st.title("🌿 Vegetarian recipe & allergen assistant")
st.caption("Understand your recipe. Explore a workable substitution.")

input_column, results_column = st.columns([1, 1.2], gap="large")

with input_column:
    st.subheader("1. Your recipe")

    st.text_area(
        "Recipe text",
        key="recipe_text",
        height=290,
        max_chars=12000,
        placeholder="Paste the ingredients and cooking instructions…",
        on_change=clear_results,
    )

    st.selectbox(
        "Allergen to remove",
        options=[None, *get_args(Allergen)],
        key="target_allergen",
        format_func=lambda value: (
            "Auto-select from recipe" if value is None else readable(value)
        ),
        on_change=clear_results,
    )

    with st.expander("Sample recipes — try an example", expanded=False):
        if DEMO_PATH.is_file():
            with DEMO_PATH.open("r", encoding="utf-8") as file:
                demo_recipes = json.load(file)

            selected_example = st.selectbox(
                "Choose a sample",
                options=range(len(demo_recipes)),
                format_func=lambda index: (
                    demo_recipes[index]["reference"]["title"]
                ),
            )

            example = demo_recipes[selected_example]
            st.code(example["input"]["recipe_text"], language=None)

            st.button(
                "Use this recipe",
                on_click=use_example,
                args=(example,),
            )
        else:
            st.info("Sample recipes are unavailable. Check the demo.json path.")

    analyse_clicked = st.button("Analyse recipe", type="primary")

    if analyse_clicked:
        clear_results()
        recipe_text = st.session_state["recipe_text"].strip()

        if len(recipe_text) < 10:
            st.warning("Enter a recipe with ingredients and instructions.")
        else:
            payload = {
                "recipe_text": recipe_text,
                "target_allergen": st.session_state["target_allergen"],
            }

            try:
                with st.spinner("Analysing the recipe and reviewing the answer…"):
                    response = httpx.post(
                        f"{API_URL}/analyse",
                        json=payload,
                        timeout=150,
                    )
                    response.raise_for_status()
                    result = response.json()

                    # Validate the backend's data before displaying it.
                    RecipeAnalysis.model_validate(result["analysis"])

                    if result["judge"] is not None:
                        JudgeAssessment.model_validate(result["judge"])

                    st.session_state["last_response"] = result

            except httpx.TimeoutException:
                st.error(
                    "The request timed out. It may still be processing; "
                    "wait before submitting again."
                )
            except httpx.HTTPStatusError as error:
                st.error(
                    f"The backend could not complete the request "
                    f"(HTTP {error.response.status_code})."
                )
            except httpx.RequestError:
                st.error("Cannot reach the backend. Check that FastAPI is running.")
            except (ValidationError, ValueError, KeyError, TypeError):
                st.error("The backend returned an unexpected response.")


with results_column:
    st.subheader("2. Analysis & substitution")

    result = st.session_state.get("last_response")

    if result is None:
        st.info("Enter a recipe or load a sample, then click Analyse recipe.")
    else:
        analysis = RecipeAnalysis.model_validate(result["analysis"])

        st.subheader(analysis.title)

        if analysis.diet in {"non_vegetarian", "uncertain"}:
            st.warning(
                "This recipe is outside the vegetarian scope, "
                "or its vegetarian suitability is uncertain."
            )

        st.write("**Diet:**", readable(analysis.diet))

        prep = analysis.prep_time_minutes
        st.write(
            "**Preparation time:**",
            "Not stated" if prep is None else f"{prep} minutes",
        )
        st.write(
            "**Difficulty:**",
            readable(analysis.difficulty) if analysis.difficulty else "Not stated",
        )

        st.markdown("#### Ingredients")
        st.write(", ".join(analysis.ingredients))

        st.markdown("#### Allergens")
        st.write("**Confirmed:**", allergen_list(analysis.allergens))
        st.write(
            "**Possible — check labels:**",
            allergen_list(analysis.possible_allergens),
        )

        st.markdown("#### Suggested substitution")
        substitution = analysis.substitution

        if substitution is None:
            st.info(
                "No substitution proposed. Check the notes for the reason."
            )
        else:
            st.write(
                "**Selected allergen:**",
                readable(analysis.main_allergen)
                if analysis.main_allergen else "Not specified",
            )

            for change in substitution.replacements:
                st.markdown(
                    f"**{change.ingredient} → {change.replacement}**"
                )
                st.write(change.adjustment)

            st.write(substitution.explanation)
            st.write(
                "**Remaining allergens:**",
                allergen_list(substitution.remaining_allergens),
            )
            st.write(
                "**Introduced allergens:**",
                allergen_list(substitution.introduced_allergens),
            )

        if analysis.notes:
            st.markdown("#### Notes")
            for note in analysis.notes:
                st.write("•", note)

        st.markdown("#### LLM judge review")

        if result["judge_status"] != "valid" or result["judge"] is None:
            st.warning(
                "The judge assessment is unavailable. "
                "The analysis above has not received a completed judge review."
            )
        else:
            judge = JudgeAssessment.model_validate(result["judge"])

            verdict_labels = {
                "decision_appropriate": "Decision appropriate",
                "allergen_removed": "Selected allergen removed",
                "dish_workable": "Dish workable",
                "vegetarian_preserved": "Remains vegetarian",
                "allergen_reporting_correct": "Allergen reporting consistent",
            }

            for field, label in verdict_labels.items():
                st.write(f"**{label}:** {readable(getattr(judge, field))}")

            st.write(judge.explanation)
            st.caption("The judge is another LLM assessment and can make mistakes.")

        with st.expander("View JSON — demo details", expanded=False):
            st.json(result)

st.divider()
st.caption(
    "Recipe-level guidance only. Check product labels and cross-contamination "
    "risks. Neither the analysis nor the judge certifies allergy safety."
)