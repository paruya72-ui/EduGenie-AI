from schemas import QARequest, QAResponse
from gemini_service import generate_text


async def answer_question(request: QARequest) -> QAResponse:
    """
    Answer a user's question using Gemini.
    """

    prompt = f"""
Answer the following question clearly and accurately.

Question:
{request.question}

Requirements:
- Give a direct answer.
- Use simple language.
- Explain important points clearly.
- If the question is technical, include a simple example when useful.
- Do not make up information.
"""

    answer = await generate_text(
        prompt=prompt,
        system_instruction=(
            "You are EduGenie, a helpful educational AI assistant. "
            "Your goal is to help students understand concepts clearly."
        ),
    )

    return QAResponse(answer=answer)