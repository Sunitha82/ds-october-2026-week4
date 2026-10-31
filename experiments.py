from time import perf_counter

from openai import APIError
from pydantic import ValidationError

from schemas import RecipeAnalysis


def run_experiment(client, deployment, messages, output_model=RecipeAnalysis):
    """Make one API attempt and return its result and measurements."""

    result = {
        "status": "not_started",
        "deployment": deployment,
        "response_seconds": None,
        "input_tokens": None,
        "output_tokens": None,
        "finish_reason": None,
        "raw_response": None,
        "validated_output": None,
        "error": None,
    }

    # Disable automatic retries for this experimental request.
    request_client = client.with_options(max_retries=0)
    start_time = perf_counter()

    try:
        response = request_client.chat.completions.create(
            model=deployment,
            messages=messages,
        )
    except APIError as error:
        result["status"] = "api_error"

        # Record the error type without copying potentially sensitive details.
        result["error"] = type(error).__name__
    else:
        choice = response.choices[0]
        result["finish_reason"] = choice.finish_reason
        result["raw_response"] = choice.message.content

        if response.usage is not None:
            result["input_tokens"] = response.usage.prompt_tokens
            result["output_tokens"] = response.usage.completion_tokens

        if getattr(choice.message, "refusal", None):
            result["status"] = "refused"
        elif choice.finish_reason != "stop":
            result["status"] = "incomplete"
        elif not choice.message.content:
            result["status"] = "empty_response"
        else:
            try:
                validated = output_model.model_validate_json(
                     choice.message.content
            )
            except ValidationError as error:
                result["status"] = "validation_error"
                result["error"] = str(error)
            else:
                result["status"] = "valid"
                result["validated_output"] = validated.model_dump()

    result["response_seconds"] = round(
        perf_counter() - start_time,
        3,
    )

    return result