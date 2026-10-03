from typing import List

from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Q&A
# ---------------------------------------------------------

class QARequest(BaseModel):
    question: str = Field(..., min_length=1)


class QAResponse(BaseModel):
    answer: str


# ---------------------------------------------------------
# Explanation
# ---------------------------------------------------------

class ExplanationRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    level: str = "beginner"


class ExplanationResponse(BaseModel):
    explanation: str


# ---------------------------------------------------------
# Quiz
# ---------------------------------------------------------

class QuizRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    level: str = "beginner"


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str


class QuizResponse(BaseModel):
    topic: str
    questions: List[QuizQuestion]


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

class SummaryRequest(BaseModel):
    text: str = Field(..., min_length=1)


class SummaryResponse(BaseModel):
    summary: str


# ---------------------------------------------------------
# Learning Path
# ---------------------------------------------------------

class LearningPathRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    level: str = "beginner"
    goal: str = "Learn the topic"


class LearningStage(BaseModel):
    stage: str
    topics: List[str]
    timeline: str
    resources: List[str]


class LearningPathResponse(BaseModel):
    topic: str
    goal: str
    stages: List[LearningStage]