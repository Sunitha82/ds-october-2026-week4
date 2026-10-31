# Vegetarian Recipe and Allergen Assistant

Week 4 assessment: NLP, Transformers and Large Language Models.

An educational LLM application that extracts recipe information and suggests
a vegetarian substitution for a selected allergen. A separate LLM call reviews
the proposed answer for allergen removal, culinary workability and reporting.

## Features

- Extracts ingredients, confirmed and possible allergens, diet, preparation
  time and difficulty into Pydantic-validated JSON.
- Compares zero-shot, few-shot and structured checklist prompting.
- Uses checklist prompting in the application, selected from development results.
- Accepts an optional target allergen; otherwise selects a confirmed allergen
  alphabetically and explains the selection.
- Handles unstated preparation time and difficulty as unknown.
- Supports vegetarian recipes, including dairy and eggs, and vegan recipes.
  Flags clearly non-vegetarian or suitability-uncertain inputs.
- Provides five demo recipes in a collapsed helper with a load button.
- Runs FastAPI and Streamlit in separate containers through Docker Compose.

This application uses an existing Azure OpenAI deployment. No model is trained
or fine-tuned, and no RAG system is used.

## Architecture

The browser connects to Streamlit on port 8501. Streamlit sends recipe text and
the requested allergen to FastAPI. FastAPI calls Azure for analysis, validates
the response, then makes a separate judge call and validates its assessment.
It returns both results to Streamlit.

Inside Compose, Streamlit uses `http://backend:8000`. Only the backend receives
Azure credentials. The LLM itself runs in Azure, not inside either container.

## Project files

| File or folder | Purpose |
|---|---|
| `recipe_allergen_assessment.ipynb` | Explanations, experiments, evaluation and conclusions |
| `schemas.py` | Recipe and judge response schemas |
| `prompts.py` | Shared rules, three prompt builders and judge prompt |
| `experiments.py` | API execution, validation and measurements |
| `api.py` | FastAPI routes and application orchestration |
| `streamlit_app.py` | Recipe interface, helper examples and result display |
| `data/vegetarian_recipe_dataset_v1/` | Synthetic recipes, reference labels and annotation guide |
| `outputs/` | Saved experiment requests, responses and scores |
| `requirements-runtime.txt` | Pinned direct application dependencies |
| `pyproject.toml`, `uv.lock` | Project environment and dependency resolution |
| `Dockerfile`, `compose.yaml` | Container build and service definitions |
| `.dockerignore`, `.gitignore` | Build-context and Git exclusions |
| `.env.example` | Configuration template containing placeholders |

## Configuration

Create a local `.env` in the project root using `.env.example` as a template.
Do not overwrite an existing working `.env`.

Set these values using your own Azure resource:

```dotenv
AZURE_OPENAI_ENDPOINT=https://YOUR_RESOURCE_NAME.openai.azure.com
AZURE_OPENAI_API_KEY=YOUR_AZURE_OPENAI_API_KEY
AZURE_OPENAI_DEPLOYMENT=YOUR_DEPLOYMENT_NAME
```

Supply the resource endpoint without `/openai/v1/`; the client appends that path.
The deployment value must match your Azure deployment name. The assessment
experiments used the deployment named `gpt-5.4-mini`.

`.env` is ignored by Git and excluded from Docker builds. Compose supplies it
to the backend at runtime. Never include real credentials in `.env.example`,
notebook outputs, screenshots or committed configuration.

## Run with Docker Compose

Prerequisites: Docker Desktop with the engine running, valid Azure configuration,
and network access to Azure and the package/image registries during build.

From the project root:

```powershell
docker compose config --quiet
docker compose up --build -d
docker compose ps
```

Open:

- App: <http://localhost:8501>
- API process health: <http://127.0.0.1:8000/health>
- API documentation: <http://127.0.0.1:8000/docs>

Stop any locally running services on ports 8000 and 8501 before starting Compose.
The frontend waits for the backend process health check; this does not check Azure.
The ports are bound to the local machine. No public hosting is configured.

To inspect logs or stop the services:

```powershell
docker compose logs --tail 50 backend frontend
docker compose down
```

After changing application code, rebuild using `docker compose up --build -d`.
After changing `.env`, recreate the backend using
`docker compose up -d --force-recreate backend`.

## Run without Docker

Prerequisites: Python 3.13, uv and a configured `.env`.

```powershell
uv sync
```

In one terminal:

```powershell
uv run uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal, from the same project root:

```powershell
uv run streamlit run streamlit_app.py
```

The frontend defaults to `http://127.0.0.1:8000`. Compose overrides this with
`API_URL=http://backend:8000` for container-to-container communication.

## Use the application

1. Paste recipe ingredients and instructions, or expand the sample helper.
2. Click **Use this recipe** to fill the input from a sample.
3. Choose a target allergen or leave auto-selection enabled.
4. Click **Analyse recipe** once.
5. Review the original recipe information, proposed adaptation, remaining and
   introduced allergens, notes and individual judge verdicts.

Loading examples does not call Azure. A successful analysis normally makes
two calls: analysis and judging. Editing inputs clears old results. A frontend
timeout does not necessarily cancel backend processing; avoid immediate repeats.

## API

| Endpoint | Behaviour |
|---|---|
| `GET /health` | Returns process health without calling Azure |
| `POST /analyse` | Accepts recipe text and an optional target; returns analysis and judge assessment |
| `GET /docs` | Interactive API documentation |

Example request:

```json
{
  "recipe_text": "Cucumber salad. Ingredients: cucumber, lemon juice, salt. Method: Slice cucumber and toss with lemon and salt.",
  "target_allergen": null
}
```

The response contains `analysis`, nullable `judge`, and `judge_status`.
`judge_status: "valid"` means the judge output passed schema validation, not
that it approved the substitution. Judge failure leaves an explicit unavailable
assessment. Invalid recipe analysis returns HTTP 502; missing configuration
returns HTTP 503; invalid request fields normally return HTTP 422.

## Dataset and evaluation

All recipes and labels were AI-authored for this assessment. They are synthetic,
consistency-checked reference data, not an independently expert-reviewed benchmark.
See the dataset README for annotation rules and limitations.

The supplied files contain 4 prompt examples, 13 development recipes, 13 test
recipes and 5 demos. To keep the assessment manageable, the executed scope was:

- First 3 prompt examples used for few-shot prompting.
- Development IDs 01, 02, 09, 10, 11 and 12: 6 recipes x 3 techniques = 18 analyses.
- Test IDs 08, 10 and 11: 3 analyses with the selected checklist prompt.
- Demo recipes kept separate from the evaluation recipes.

The same deployment, recipe inputs and output schema were used across techniques.
Checklist instructions were refined using exploratory development observations;
the comparison is not a controlled estimate of the prompting style alone.

API attempts have automatic retries disabled. Original responses, failures,
timing, token usage and request definitions are saved. Unchanged batch reruns
skip saved attempts, including failures. Changed request definitions create new
result folders. Earlier exploratory cells can make new calls if rerun.

### Development results

Counts below are out of six original attempts per technique.

| Technique | Schema-valid | Confirmed allergens correct | Diet correct | Prep time correct | Difficulty correct | Judge-approved answers |
|---|---:|---:|---:|---:|---:|---:|
| Zero-shot | 5 | 5 | 4 | 5 | 5 | 2 |
| Few-shot | 6 | 6 | 6 | 6 | 6 | 3 |
| Checklist | 6 | 6 | 6 | 6 | 6 | 4 |

Allergen scoring uses exact set equality. The other extraction scores use exact
reference matches, including null for unstated values. Invalid analyses receive
no successful field scores because the application cannot accept them; this is
an application-level scoring choice, not a claim that every raw field was wrong.

The judge used a fixed rubric and a separate call to the same deployment.
It received the original input and candidate answer, without the technique name
or reference substitution. All 17 schema-valid development answers were judged;
one trial was reused. All 17 judge responses passed their schema.

Judge approval requires all applicable checks to pass. No-substitution answers
are assessed for correct withholding and reporting, so approved counts include
those cases, not just successful substitutions. Uncertainty is not approval.
Manual review found weak or partly incorrect judge objections. Original scores
were preserved, with qualifications recorded separately in the notebook.

### Selection and held-out results

Checklist prompting was selected because it matched all measured development
extraction fields, had no schema failures, and had the highest recorded judge
approval. This is a practical choice for the assessment, not proof of superiority.

On three held-out recipes, checklist achieved 3/3 for schema validity, confirmed
allergens, diet, preparation time and difficulty. Test substitutions were manually
inspected; no separate held-out judge score is claimed. The selected prompt was
not tuned after inspecting these results.

Observed limitations included confusing cross-contact wording and an unsupported
assumption that a replacement couscous product uses identical hydration instructions.
The app also demonstrated a judge challenge to an ambiguous tamari-style option.

### Reproduce or inspect experiments

Open the notebook from the project root and select the project's `.venv` Python
kernel, rather than a separate global Python installation. Run cells in order.
Saved cell output does not recreate Python variables after a kernel restart.

Inspection and scoring cells use existing data without API calls. Connection,
exploratory analysis, experiment and judge cells may incur Azure usage. For the
recorded development run, results are under
`outputs/development_comparison_a7418792c152/`; final test results are under
`outputs/final_test_6700715e5cce/`. Fresh executions can produce different outputs.

## Verification status

- Dataset loading and structural checks completed.
- Pydantic accepted a valid example and rejected invalid diet, negative time
  and missing required-field examples.
- Azure connection and recorded experiments completed.
- Local FastAPI health and analysis requests succeeded.
- Local Streamlit interaction and judge display were exercised.
- Compose showed both services running and the backend healthy; the Docker UI loaded.
- Final confirmation of a recipe analysis plus judge review through the Docker
  UI is still pending at the time this README was prepared.
- GitHub push and presentation preparation remain pending.

## Limits

This is an educational prototype, not an allergy-safety certification tool.
Product ingredients and cross-contamination require separate checking. Vegetarian
does not mean allergen-free. Removing one allergen may leave or introduce others.

The evaluation uses six development and three test recipes, with one recorded
attempt per recipe/technique. It does not establish statistical reliability,
latency superiority or full coverage of every allergen category. The schemas
use a UK-14-aligned vocabulary; the evaluated subset does not cover all categories
and this project does not claim regulatory compliance.

Ingredient extraction and possible-allergen reasoning were not comprehensively
scored in the reported extraction table. Difficulty was extracted when stated,
not independently estimated. Both the assistant and same-model judge can make
mistakes. Judge failures are displayed but do not automatically repair answers.

Direct runtime dependencies are version-pinned; transitive dependencies and the
base image are not completely frozen by `requirements-runtime.txt` alone.

## Before submitting

- Complete the final Docker recipe check and update verification status.
- Save the executed notebook and final conclusion.
- Keep the labelled data and relevant synthetic evaluation outputs in the repository.
- Verify `.env` is ignored and untracked; commit only placeholder configuration.
- Review staged files, push to GitHub and add the repository link to the assessment card.
- Prepare the presentation and a short demonstration using the sample helper.
