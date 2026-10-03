from schemas import QuizRequest, QuizResponse
from gemini_service import generate_structured


async def generate_quiz(request: QuizRequest) -> QuizResponse:
    """
    Generate a quiz for the requested topic and difficulty level.
    """

    prompt = f"""
Create a multiple-choice quiz for a student.

Topic:
{request.topic}

Student level:
{request.level}

Requirements:
- Generate exactly 3 questions.
- Each question must have exactly 4 options.
- Each question must have one correct answer.
- Provide a short explanation for the correct answer.
- Keep the questions appropriate for the student's level.
- Make the questions educational and clear.
- Do not include duplicate questions.

Return the result using the required structured format.
"""

    return await generate_structured(
        prompt=prompt,
        response_schema=QuizResponse,
        system_instruction=(
            "You are EduGenie, an educational quiz generator. "
            "Create accurate and useful multiple-choice questions "
            "for students."
        ),
    )