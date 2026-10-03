from schemas import LearningPathRequest, LearningPathResponse
from gemini_service import generate_structured


async def generate_learning_path(
    request: LearningPathRequest,
) -> LearningPathResponse:
    """
    Generate a personalized learning path for the student.
    """

    prompt = f"""
Create a personalized learning path for a student.

Topic:
{request.topic}

Current level:
{request.level}

Learning goal:
{request.goal}

Requirements:
- Organize the learning path from beginner to advanced.
- Divide the path into clear stages.
- Include important topics in each stage.
- Give a realistic timeline for each stage.
- Suggest useful learning resources for each stage.
- Keep the plan practical and easy to follow.
- Make the recommendations appropriate for the student's level.
- Do not include unnecessary topics.

Return the result using the required structured format.
"""

    return await generate_structured(
        prompt=prompt,
        response_schema=LearningPathResponse,
        system_instruction=(
            "You are EduGenie, a personalized educational "
            "learning-path assistant. Create structured, "
            "practical learning plans for students."
        ),
    )