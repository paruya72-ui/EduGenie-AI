from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from schemas import (
    QARequest,
    QAResponse,
    ExplanationRequest,
    ExplanationResponse,
    QuizRequest,
    QuizResponse,
    SummaryRequest,
    SummaryResponse,
    LearningPathRequest,
    LearningPathResponse,
)

from qna import answer_question
from explanation_module import explain_concept
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import generate_learning_path
from gemini_service import GeminiConfigurationError


app = FastAPI(
    title="EduGenie",
    description="Google Gemini Powered Learning Assistant",
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "application": "EduGenie",
    }


@app.post("/qa", response_model=QAResponse)
async def qa(request: QARequest):
    try:
        return await answer_question(request)

    except GeminiConfigurationError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    except Exception as exc:
        error_text = str(exc)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini daily request quota has been reached. "
                    "Please try again after the quota resets."
                ),
            )

        if "503" in error_text or "UNAVAILABLE" in error_text:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Gemini is temporarily busy. "
                    "Please try again later."
                ),
            )

        raise HTTPException(
            status_code=500,
            detail=f"Unable to answer the question: {exc}",
        )


@app.post("/explain", response_model=ExplanationResponse)
async def explain(request: ExplanationRequest):
    try:
        return await explain_concept(request)

    except GeminiConfigurationError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    except Exception as exc:
        error_text = str(exc)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini daily request quota has been reached. "
                    "Please try again after the quota resets."
                ),
            )

        if "503" in error_text or "UNAVAILABLE" in error_text:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Gemini is temporarily busy. "
                    "Please try again later."
                ),
            )

        raise HTTPException(
            status_code=500,
            detail=f"Unable to explain the concept: {exc}",
        )


@app.post("/quiz", response_model=QuizResponse)
async def quiz(request: QuizRequest):
    try:
        return await generate_quiz(request)

    except GeminiConfigurationError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    except Exception as exc:
        error_text = str(exc)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini daily request quota has been reached. "
                    "Please try again after the quota resets."
                ),
            )

        if "503" in error_text or "UNAVAILABLE" in error_text:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Gemini is temporarily busy. "
                    "Please try again later."
                ),
            )

        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate the quiz: {exc}",
        )


@app.post("/summarize", response_model=SummaryResponse)
async def summarize(request: SummaryRequest):
    try:
        return await summarize_text(request)

    except GeminiConfigurationError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    except Exception as exc:
        error_text = str(exc)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini daily request quota has been reached. "
                    "Please try again after the quota resets."
                ),
            )

        if "503" in error_text or "UNAVAILABLE" in error_text:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Gemini is temporarily busy. "
                    "Please try again later."
                ),
            )

        raise HTTPException(
            status_code=500,
            detail=f"Unable to summarize the text: {exc}",
        )


@app.post(
    "/learn/recommendations",
    response_model=LearningPathResponse,
)
async def learning_recommendations(
    request: LearningPathRequest,
):
    try:
        return await generate_learning_path(request)

    except GeminiConfigurationError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    except Exception as exc:
        error_text = str(exc)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini daily request quota has been reached. "
                    "Please try again after the quota resets."
                ),
            )

        if "503" in error_text or "UNAVAILABLE" in error_text:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Gemini is temporarily busy. "
                    "Please try again later."
                ),
            )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to generate learning recommendations: "
                f"{exc}"
            ),
        )