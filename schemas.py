from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# Standard names prevent variations such as "dairy" versus "milk".
Allergen = Literal[
    "celery",
    "cereals_containing_gluten",
    "crustaceans",
    "eggs",
    "fish",
    "lupin",
    "milk",
    "molluscs",
    "mustard",
    "nuts",
    "peanuts",
    "sesame",
    "soya",
    "sulphur_dioxide_and_sulphites",
]


class StrictModel(BaseModel):
    """Reject unexpected fields and automatic type conversions."""

    model_config = ConfigDict(extra="forbid", strict=True)


class IngredientReplacement(StrictModel):
    """One ingredient change within the overall substitution plan."""

    ingredient: str = Field(min_length=1)
    replacement: str = Field(min_length=1)
    adjustment: str = Field(
        min_length=1,
        description="Quantity or method adjustment, or state none needed.",
    )


class Substitution(StrictModel):
    """A plan that must address every source of the selected allergen."""

    replacements: list[IngredientReplacement] = Field(min_length=1)
    explanation: str = Field(min_length=1)
    remaining_allergens: list[Allergen]
    introduced_allergens: list[Allergen]


class RecipeAnalysis(StrictModel):
    """Structured analysis of the original recipe and a proposed change."""

    title: str = Field(min_length=1)
    ingredients: list[str] = Field(min_length=1)

    # These describe the ORIGINAL recipe.
    allergens: list[Allergen]
    possible_allergens: list[Allergen]
    diet: Literal["vegan", "vegetarian", "non_vegetarian", "uncertain"]
    prep_time_minutes: int | None = Field(ge=0)
    difficulty: Literal["easy", "medium", "hard"] | None

    # These describe the proposed adaptation.
    main_allergen: Allergen | None
    substitution: Substitution | None

    # Explain uncertainty, label checks or unsuitable input.
    notes: list[str]

JudgeVerdict = Literal["yes", "no", "uncertain", "not_applicable"]


class JudgeAssessment(StrictModel):
    """Structured review of a recipe assistant's proposed adaptation."""

    decision_appropriate: Literal["yes", "no", "uncertain"]
    allergen_removed: JudgeVerdict
    dish_workable: JudgeVerdict
    vegetarian_preserved: JudgeVerdict
    allergen_reporting_correct: Literal["yes", "no", "uncertain"]
    explanation: str = Field(min_length=1)