# Vegetarian recipe dataset v1 — assessment starter benchmark

## Provenance and status
Created 30 October 2026. All recipes and reference labels are AI-authored synthetic
educational examples, not scraped recipes, observed user data or expert-certified
allergy guidance. Labels have received a consistency check but have NOT been
independently reviewed by a human or food-allergy specialist. Review and correct
them before freezing the benchmark. No model performance has been measured.

## Files and use
| File | Records | Purpose |
|---|---:|---|
| examples.json | 4 | Few-shot prompt demonstrations only; never scored |
| development.json | 13 | Compare all three prompting techniques and tune prompts |
| test.json | 13 | Final evaluation of the selected, frozen prompt; no tuning |
| demo.json | 5 | UI helper recipes; never counted as test results |

Each file contains a JSON array. JSON preserves lists and unknown/null values
without awkward CSV cell encoding. Only send record['input'] to the LLM.
Never include record['reference'], provenance, ID or split in a model request.
For few-shot examples, the example reference may be used to construct expected
assistant messages after mapping it to the agreed response schema.

## Field dictionary
- recipe_id: stable identifier within v1.
- split: predefined role; do not randomly resplit while experimenting.
- recipe_family: grouping key; each authored family occurs in one split only.
- input.recipe_text: actual recipe text including ingredients and method.
- input.target_allergen: explicit requested allergen, or null for auto-selection.
- reference.ingredients: canonical ingredient names; quantity is in the input,
  not part of the initial exact ingredient-name evaluation.
- reference.allergens: definite ingredient-level categories supported by the input.
- reference.possible_allergens: uncertainty flags, NOT confirmed positives.
- reference.diet: mutually exclusive vegan / vegetarian / uncertain.
  'vegetarian' means vegetarian but not established vegan; it includes recipes
  explicitly vegetarian with unresolved vegan status, explained in notes.
- reference.prep_time_minutes: explicitly stated preparation time; excludes
  cooking time. Null means unstated, not zero.
- reference.difficulty: explicitly stated easy/medium/hard, or null if unstated.
  For this benchmark, do not score a guessed difficulty as a reference fact.
  A later app estimate must be separately marked as estimated.
- reference.main_allergen: equals the explicit requested target for positive cases.
- reference.substitution_required: false when no definite target exists.
- reference.substitution_reference: acceptable example changes, introduced
  allergens and remaining original allergens; NOT a unique correct wording.
- reference.annotation_notes: ambiguity and evaluation caveats for that recipe.

## Annotation rules
1. Evaluate the written recipe, not a usual/traditional version of that dish.
2. Quantities are illustrative. Do not infer nutrition or cooking guarantees.
3. Retain pantry ingredients such as salt, oil and explicitly listed water.
4. Map milk, butter, cream, yoghurt, paneer and explicitly dairy cheeses to milk.
5. Separate peanuts from tree nuts ('nuts'). Coconut is not a UK-14 tree nut.
6. Wheat, wheat pasta, wheat bread and wheat couscous map to
   cereals_containing_gluten. Rice, maize/polenta and quinoa do not map there.
7. Tofu and edamame map to soya. Tahini, sesame seeds and sesame oil map to sesame.
8. Celeriac maps to celery. Mustard seeds/powder map to mustard. Lupin flour maps
   to lupin. Chickpea is not lupin; do not infer individual cross-reactivity.
9. Explicitly specified compound ingredients use only the stated composition.
   Ingredient lists here are closed educational assumptions, not a claim that
   commercial products always have those contents.
10. Unspecified stock, pesto and cheese require label/suitability checks. Do not
    convert possible allergens to definite ones. Possible lists are conservative
    label-check hints, not exhaustive manufacturer ingredient statements.
11. Vegan is also vegetarian, but use the single most specific diet label.
    Unknown cheese rennet can make vegetarian suitability uncertain.
12. Unknown preparation time and difficulty stay null. Do not confuse preparation
    time with cooking or total time.
13. Positive cases have an explicit target so all prompt variants address the same
    allergen. Auto-selection with multiple definite allergens is a separate UI
    behaviour to test later, not measured by this dataset.
14. Remove ALL listed sources of the selected allergen. Replacing butter while
    leaving cream, or sesame seeds while leaving sesame oil, fails removal.
15. Other allergens may remain; disclose them. New allergens must be disclosed.
    Replacing milk with tofu can remove milk but introduce soya.
16. No definite allergens means no substitution is required, not 'allergy safe'.
    Where only possible allergens exist, request/check the product label.
17. Diet-uncertain recipes are intentional boundary cases. Flag uncertainty rather
    than silently admitting them as definitely vegetarian.

## Judge rubric (proposed; not a measured result)
The judge receives the original recipe, selected allergen and candidate answer.
It should NOT receive prompt-technique names, reference replacements or prior
scores. Use the same judge instructions for every variant.
- Removal: yes/no/uncertain — are all selected-allergen sources addressed, and
  does the replacement avoid it under its stated ingredients?
- Workability: yes/no/uncertain — can the dish work with stated quantity/method
  adjustments? Does the suggestion preserve the ingredient's practical role?
- Vegetarian suitability: yes/no/uncertain.
- Introduced/remaining allergens disclosed: yes/no/uncertain.
- Short evidence-based explanation citing ingredients, not hidden reasoning.
Judge outputs require their own Pydantic schema. Treat the judge as fallible;
manually inspect its assessments, including failures and uncertainty cases.
Do not require literal matches to the reference substitution. Other valid
replacements are acceptable. An uncertain answer is not an automatic pass.

## Evaluation plan
Use ingredient-name normalisation and explicit synonym mappings fixed on the
development set; do not invent fuzzy matching after inspecting test failures.
Report definite-allergen precision, recall and F1 separately from uncertainty
flags. For no-allergen records, distinguish empty-set success from missing data.
Score diet, stated prep time and stated difficulty independently; report unknown
handling separately. Record Pydantic first-attempt success, retries, failures,
latency and token usage. Do not silently drop invalid or failed requests.
Score acceptable substitutions with the rubric, not a string comparison.
No fine-tuning/training set is needed: 'examples' means prompt examples.
Freeze labels, prompts, model settings and scoring rules before opening test
results. Do not put benchmark test recipes in the UI demo helper or few-shot
prompt. Shared common ingredients across splits are expected; the same recipe
or close paraphrase should not cross splits. Recipe families were separated by
authoring, not by a semantic-similarity audit.

## Limits and coverage
30 benchmark records (4 examples + 13 development + 13 test), plus 5 demos.
This is a small, intentionally varied educational benchmark, not a statistically
representative sample. It has ten definite allergen categories, not full positive
coverage of all 14. Fish, crustaceans and molluscs are outside vegetarian inputs;
sulphites have no positive cases because concentration-dependent labelling is
not established by these recipes. There are no 'hard' difficulty examples.
Do not claim 14-category validation, production reliability, nutrition matching,
cross-contamination detection or clinical safety from these results.
The category vocabulary is a proposed UK-14-aligned taxonomy; current official
guidance could not be retrieved during generation and must be checked before
finalising terminology or making UK compliance claims.

## Local project placement
Extract this folder into your Week 4 project and keep it under data/.
Keep labels out of prompts except for the examples partition. Keep Azure keys
in .env, never in this dataset or Git. Next notebook step: load, inspect and
review the development/example labels before implementing prompts.
