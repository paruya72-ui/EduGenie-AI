from schemas import ExplanationRequest, ExplanationResponse
from gemini_service import generate_text


async def explain_concept(
    request: ExplanationRequest,
) -> ExplanationResponse:
    """
    Explain a concept according to the learner's level.
    """

    prompt = f"""
Explain the following concept to a student.

Topic:
{request.topic}

Student level:
{request.level}

Requirements:
- Start with a simple definition.
- Explain the concept step by step.
- Use simple language.
- Give a practical example when useful.
- Mention important points the student should remember.
- Avoid unnecessary complexity.
"""

    explanation = await generate_text(
        prompt=prompt,
        system_instruction=(
            "You are EduGenie, an educational AI assistant. "
            "Explain concepts clearly and adapt explanations "
            "to the student's requested level."
        ),
    )

    return ExplanationResponse(
        explanation=explanation
    )