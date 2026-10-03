from schemas import SummaryRequest, SummaryResponse
from gemini_service import generate_text


async def summarize_text(
    request: SummaryRequest,
) -> SummaryResponse:
    """
    Summarize the text provided by the user.
    """

    prompt = f"""
Summarize the following educational text.

Text:
{request.text}

Requirements:
- Keep the important information.
- Remove unnecessary repetition.
- Use clear and simple language.
- Organize the summary logically.
- Do not add information that is not present in the original text.
- Keep the summary shorter than the original text.
"""

    summary = await generate_text(
        prompt=prompt,
        system_instruction=(
            "You are EduGenie, an educational AI assistant. "
            "Summarize learning material accurately and clearly "
            "without changing its meaning."
        ),
    )

    return SummaryResponse(
        summary=summary
    )