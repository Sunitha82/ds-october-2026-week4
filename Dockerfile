FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-runtime.txt .
RUN pip install --no-cache-dir -r requirements-runtime.txt

COPY api.py experiments.py prompts.py schemas.py streamlit_app.py ./
COPY data/vegetarian_recipe_dataset_v1/demo.json ./data/vegetarian_recipe_dataset_v1/demo.json

RUN useradd --create-home appuser
USER appuser

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]