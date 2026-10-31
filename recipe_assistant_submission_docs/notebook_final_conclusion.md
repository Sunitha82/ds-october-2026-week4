## 30. Final Findings and Conclusion

### Assessment outcome

We built a vegetarian recipe and allergen assistant using an existing Azure
OpenAI deployment. We did not train or fine-tune a model.

The project demonstrates three prompting techniques, labelled evaluation,
Pydantic-validated JSON, an LLM judge, a FastAPI backend, a Streamlit frontend
and separate containers managed by Docker Compose.

### Development comparison

We compared each technique on the same six development recipes. The few-shot
prompt used three separate worked examples. The test set was not used to tune
the prompts. Checklist instructions incorporated exploratory development findings.

| Technique | Schema-valid | Confirmed allergens correct | Diet correct | Prep time correct | Difficulty correct | Judge-approved |
|---|---:|---:|---:|---:|---:|---:|
| Zero-shot | 5/6 | 5/6 | 4/6 | 5/6 | 5/6 | 2/6 |
| Few-shot | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 3/6 |
| Checklist | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 4/6 |

Invalid analyses received no successful field scores, even if some raw values
were correct, because the application could not accept the full response.

### Selected approach

We selected structured checklist prompting. It matched every measured extraction
field, produced six schema-valid responses and had the highest recorded judge
approval. The app reuses this prompt and the same response schemas.

This is a practical assessment decision. The small sample does not prove that
checklist prompting will always outperform few-shot prompting.

### Held-out evaluation

The frozen checklist prompt was evaluated on TEST_08, TEST_10 and TEST_11.

| Check | Result |
|---|---:|
| Schema validity | 3/3 |
| Confirmed allergen set | 3/3 |
| Diet classification | 3/3 |
| Preparation time, including unknown handling | 3/3 |
| Difficulty, including unknown handling | 3/3 |

Manual inspection found that the sesame case addressed both sesame oil and
sesame seeds, the couscous case retained the milk warning for feta, and the
no-allergen case correctly withheld a substitution. Limitations remained:
cross-contact wording was confusing, and the couscous replacement assumed the
same hydration instructions without establishing the replacement product's needs.

No separate LLM-judge score is claimed for the held-out set. The selected prompt
was not changed in response to these test results.

### What Pydantic and the judge contributed

Pydantic caught an omitted notes field. It also accepted some factually incorrect
responses, showing that schema validation does not establish factual correctness.

The LLM judge reviewed the 17 schema-valid development answers using a fixed
rubric. It helped flag incomplete or ambiguous allergen reporting and unclear
substitution instructions. All 17 judge responses passed schema validation.

Judge-approved counts include appropriate no-substitution decisions. For a
substitution to pass, every applicable criterion had to be yes; uncertain was
not a pass. The invalid analysis remained a failure in the six-attempt denominator.

Manual review identified weak or partly incorrect judge objections, including
the sunflower-seed assessment and criticism of reporting soya for tofu. We kept
the original judge scores and recorded these qualifications separately.

The judge used a separate call to the same deployed model. This can share errors
with the original analysis; it is not an independent safety authority.

### Deployment

The local API and Streamlit interface were exercised. Docker Compose showed two
running services, with a healthy backend, and the Docker UI loaded.

Final confirmation that a recipe produces both analysis and judge review through
the Docker UI is pending. GitHub submission and presentation preparation are also
pending. Update this status after those actions are completed.

### Limitations

- Synthetic AI-authored reference labels were not independently expert-reviewed.
- Six development recipes and three held-out recipes provide limited evidence.
- Ingredient extraction and possible-allergen reasoning were not comprehensively
  scored by the reported extraction metrics.
- No complete allergen-category coverage or regulatory compliance is claimed.
- Difficulty was extracted when stated; missing time and difficulty remained null.
- Responses can vary between calls. Single-request timings do not establish a
  reliable speed or cost advantage.
- Brand-specific ingredients, individual sensitivities and cross-contamination
  cannot be resolved from recipe text alone.
- A failed or negative judge review does not automatically repair the answer.

### Conclusion

The assessment shows how prompt design, labelled evaluation, structural
validation and a separate judge can be combined in a working LLM application.
Checklist prompting was the best supported choice in this small comparison,
while the observed errors show why every layer needs explicit limitations.

The assistant is an educational recipe-analysis tool, not an assurance that a
dish is safe for someone with an allergy.
