import asyncio
import json
import re
from typing import Type, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_INPUT_CHARS,
)


T = TypeVar("T", bound=BaseModel)


class GeminiConfigurationError(Exception):
    """Raised when Gemini is not configured correctly."""


def get_client():
    if not GEMINI_API_KEY:
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is missing. "
            "Please add your Gemini API key to the .env file."
        )

    return genai.Client(api_key=GEMINI_API_KEY)


def limit_text(text: str) -> str:
    text = text.strip()

    if len(text) > MAX_INPUT_CHARS:
        return text[:MAX_INPUT_CHARS]

    return text


def is_gemini_unavailable(error: Exception) -> bool:
    """
    Detect Gemini quota and temporary availability errors.
    """

    error_text = str(error).upper()

    return (
        "429" in error_text
        or "RESOURCE_EXHAUSTED" in error_text
        or "503" in error_text
        or "UNAVAILABLE" in error_text
    )


async def call_gemini_text(
    prompt: str,
    system_instruction: str | None = None,
) -> str:

    client = get_client()

    config = types.GenerateContentConfig(
        temperature=0.4,
    )

    if system_instruction:
        config.system_instruction = system_instruction

    response = await client.aio.models.generate_content(
        model=GEMINI_MODEL,
        contents=limit_text(prompt),
        config=config,
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response.text.strip()


async def call_gemini_structured(
    prompt: str,
    response_schema: Type[T],
    system_instruction: str | None = None,
) -> T:

    client = get_client()

    config = types.GenerateContentConfig(
        temperature=0.3,
        response_mime_type="application/json",
        response_schema=response_schema,
    )

    if system_instruction:
        config.system_instruction = system_instruction

    response = await client.aio.models.generate_content(
        model=GEMINI_MODEL,
        contents=limit_text(prompt),
        config=config,
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini returned invalid JSON."
        ) from exc

    try:
        return response_schema.model_validate(data)
    except Exception as exc:
        raise RuntimeError(
            "Gemini response did not match "
            "the expected format."
        ) from exc


async def generate_text(
    prompt: str,
    system_instruction: str | None = None,
) -> str:
    """
    Generate text using Gemini.

    If Gemini is temporarily unavailable or the
    free quota is exhausted, return a local fallback.
    """

    try:

        return await call_gemini_text(
            prompt=prompt,
            system_instruction=system_instruction,
        )

    except GeminiConfigurationError:
        raise

    except Exception as exc:

        if is_gemini_unavailable(exc):

            return generate_local_text_fallback(prompt)

        raise


async def generate_structured(
    prompt: str,
    response_schema: Type[T],
    system_instruction: str | None = None,
) -> T:
    """
    Generate structured data using Gemini.

    If Gemini is unavailable, create a local fallback
    for supported EduGenie structured features.
    """

    try:

        return await call_gemini_structured(
            prompt=prompt,
            response_schema=response_schema,
            system_instruction=system_instruction,
        )

    except GeminiConfigurationError:
        raise

    except Exception as exc:

        if is_gemini_unavailable(exc):

            return generate_local_structured_fallback(
                prompt,
                response_schema,
            )

        raise


def extract_value(
    prompt: str,
    label: str,
    default: str,
) -> str:

    pattern = rf"{re.escape(label)}\s*:\s*(.+)"

    match = re.search(
        pattern,
        prompt,
        re.IGNORECASE,
    )

    if match:

        value = match.group(1).strip()

        if value:
            return value.split("\n")[0].strip()

    return default


def generate_local_text_fallback(
    prompt: str,
) -> str:
    """
    Local fallback for Q&A, explanation and summary.
    """

    prompt_lower = prompt.lower()

    # -------------------------------------------------
    # SUMMARY
    # -------------------------------------------------

    if "summarize" in prompt_lower:

        text = extract_value(
            prompt,
            "Text",
            "No text was provided.",
        )

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        if len(sentences) > 3:
            summary_sentences = sentences[:3]
        else:
            summary_sentences = sentences

        if not summary_sentences:
            return (
                "The provided text could not be summarized."
            )

        return (
            "Local Summary:\n\n"
            + " ".join(summary_sentences)
            + "\n\n"
            "Note: Gemini is currently unavailable, "
            "so EduGenie generated this basic local summary."
        )

    # -------------------------------------------------
    # EXPLANATION
    # -------------------------------------------------

    if "explain" in prompt_lower:

        topic = extract_value(
            prompt,
            "Topic",
            "the requested concept",
        )

        return (
            f"Understanding {topic}\n\n"
            f"Definition:\n"
            f"{topic} is an important concept that can "
            f"be understood by learning its basic meaning "
            f"and how it is used.\n\n"
            f"How to learn it:\n"
            f"1. Understand the basic definition.\n"
            f"2. Learn the main parts or features.\n"
            f"3. Study a simple example.\n"
            f"4. Practice using the concept.\n"
            f"5. Review what you learned.\n\n"
            f"Example:\n"
            f"Try a small practical exercise related to "
            f"{topic} to understand how it works.\n\n"
            "Note: Gemini is currently unavailable, "
            "so EduGenie generated this local explanation."
        )

    # -------------------------------------------------
    # Q&A
    # -------------------------------------------------

    question = extract_value(
        prompt,
        "Question",
        "your question",
    )

    question_lower = question.lower()

    # Common educational questions
    if "what is html" in question_lower:

        return (
            "HTML stands for HyperText Markup Language. "
            "It is used to create the structure of web "
            "pages.\n\n"
            "For example:\n\n"
            "<h1>Hello World</h1>\n\n"
            "The <h1> element creates a main heading."
        )

    if "what is css" in question_lower:

        return (
            "CSS stands for Cascading Style Sheets. "
            "It is used to style and design HTML web pages.\n\n"
            "CSS can control colors, fonts, spacing, "
            "layouts, borders and animations."
        )

    if "what is javascript" in question_lower:

        return (
            "JavaScript is a programming language commonly "
            "used to make web pages interactive.\n\n"
            "For example, JavaScript can respond to button "
            "clicks, change page content and validate forms."
        )

    if "what is python" in question_lower:

        return (
            "Python is a high-level programming language "
            "known for its simple and readable syntax.\n\n"
            "It is commonly used for web development, "
            "automation, data analysis, machine learning "
            "and artificial intelligence."
        )

    if "what is ai" in question_lower:

        return (
            "Artificial Intelligence, or AI, is technology "
            "that enables computers to perform tasks that "
            "normally require human-like intelligence.\n\n"
            "Examples include language understanding, "
            "image recognition and recommendation systems."
        )

    return (
        f"Your question is:\n\n"
        f"{question}\n\n"
        "EduGenie is currently using its local fallback "
        "because the Gemini API quota is unavailable.\n\n"
        "Try asking about HTML, CSS, JavaScript, Python, "
        "AI or another programming concept. Once the "
        "Gemini quota becomes available, EduGenie will "
        "automatically use Gemini again."
    )


def generate_local_structured_fallback(
    prompt: str,
    response_schema: Type[T],
) -> T:
    """
    Local fallback for Quiz and Learning Path.
    """

    schema_name = response_schema.__name__.lower()

    topic = extract_value(
        prompt,
        "Topic",
        "Web Development",
    )

    level = extract_value(
        prompt,
        "Student level",
        "beginner",
    )

    if "quizresponse" in schema_name:

        return create_local_quiz(
            topic=topic,
            level=level,
            response_schema=response_schema,
        )

    if "learningpathresponse" in schema_name:

        goal = extract_value(
            prompt,
            "Learning goal",
            "Learn the topic",
        )

        return create_local_learning_path(
            topic=topic,
            level=level,
            goal=goal,
            response_schema=response_schema,
        )

    raise RuntimeError(
        "No local fallback is available for this "
        "structured response type."
    )


def create_local_quiz(
    topic: str,
    level: str,
    response_schema: Type[T],
) -> T:

    questions = [
        {
            "question": f"What is the main purpose of learning {topic}?",
            "options": [
                "To understand and apply the concept",
                "To avoid practicing",
                "To remove all learning",
                "None of these",
            ],
            "correct_answer": (
                "To understand and apply the concept"
            ),
            "explanation": (
                f"Learning {topic} helps you understand "
                "its concepts and apply them in practical "
                "situations."
            ),
        },
        {
            "question": (
                f"Which approach is useful when learning {topic}?"
            ),
            "options": [
                "Practice with examples",
                "Never practice",
                "Skip the basics",
                "Memorize everything without understanding",
            ],
            "correct_answer": "Practice with examples",
            "explanation": (
                "Practical examples help learners "
                "understand and remember concepts."
            ),
        },
        {
            "question": (
                f"What should a beginner do first when learning {topic}?"
            ),
            "options": [
                "Learn the fundamentals",
                "Start with the hardest topic",
                "Skip all explanations",
                "Stop practicing",
            ],
            "correct_answer": "Learn the fundamentals",
            "explanation": (
                "Understanding the fundamentals creates "
                "a strong foundation for advanced topics."
            ),
        },
    ]

    data = {
        "topic": topic,
        "questions": questions,
    }

    return response_schema.model_validate(data)


def create_local_learning_path(
    topic: str,
    level: str,
    goal: str,
    response_schema: Type[T],
) -> T:

    data = {
        "topic": topic,
        "goal": goal,
        "stages": [
            {
                "stage": "Fundamentals",
                "topics": [
                    f"Introduction to {topic}",
                    "Basic terminology",
                    "Core concepts",
                    "Basic practice",
                ],
                "timeline": "1-2 weeks",
                "resources": [
                    "Official documentation",
                    "Beginner tutorials",
                    "Simple practice exercises",
                ],
            },
            {
                "stage": "Intermediate",
                "topics": [
                    f"Intermediate {topic} concepts",
                    "Practical projects",
                    "Problem solving",
                    "Common tools and techniques",
                ],
                "timeline": "2-4 weeks",
                "resources": [
                    "Intermediate tutorials",
                    "Practice projects",
                    "Documentation and examples",
                ],
            },
            {
                "stage": "Advanced",
                "topics": [
                    f"Advanced {topic} concepts",
                    "Real-world projects",
                    "Performance and best practices",
                    "Portfolio project",
                ],
                "timeline": "4-8 weeks",
                "resources": [
                    "Advanced documentation",
                    "Real-world projects",
                    "Open-source examples",
                ],
            },
        ],
    }

    return response_schema.model_validate(data)