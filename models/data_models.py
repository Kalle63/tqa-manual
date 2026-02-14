from pydantic import BaseModel, Field


# The 12 error types from the scorecard
ERROR_TYPES = [
    "Punctuation",
    "Grammar",
    "Spelling",
    "Terminology",
    "Style",
    "Unidiomatic",
    "Untranslated",
    "Major Mistranslation",
    "Critical Mistranslation",
    "Omission",
    "Numerical Error",
]

# Error type numbers matching the scorecard (note: no #4)
ERROR_TYPE_NUMBERS = {
    "Punctuation": 1,
    "Grammar": 2,
    "Spelling": 3,
    "Terminology": 5,
    "Style": 6,
    "Unidiomatic": 7,
    "Untranslated": 8,
    "Major Mistranslation": 9,
    "Critical Mistranslation": 10,
    "Omission": 11,
    "Numerical Error": 12,
}

SEVERITY_LEVELS = ["Minor", "Major", "Critical"]

# Severity penalty multipliers
SEVERITY_PENALTIES = {
    "Minor": 1,
    "Major": 5,
    "Critical": 10,
}

# Default severity for each error type (guidance for Claude)
DEFAULT_SEVERITIES = {
    "Punctuation": "Minor",
    "Grammar": "Minor",
    "Spelling": "Minor",
    "Terminology": "Major",
    "Style": "Major",
    "Unidiomatic": "Major",
    "Untranslated": "Major",
    "Major Mistranslation": "Major",
    "Critical Mistranslation": "Critical",
    "Omission": "Critical",
    "Numerical Error": "Critical",
}


class ErrorAnnotation(BaseModel):
    """A single error annotation on a target segment."""

    error_type: str = Field(
        description="One of: Punctuation, Grammar, Spelling, Terminology, Style, "
        "Unidiomatic, Untranslated, Major Mistranslation, Critical Mistranslation, "
        "Omission, Numerical Error"
    )
    severity: str = Field(description="Severity level: Minor, Major, or Critical")
    span: str = Field(
        description="The exact span of text in the target that contains the error"
    )
    explanation: str = Field(description="Brief explanation of the error")


class SegmentAssessment(BaseModel):
    """Claude's full assessment of a single source-target pair."""

    annotations: list[ErrorAnnotation] = Field(
        default_factory=list, description="List of error annotations found"
    )
    overall_comment: str = Field(
        default="", description="Brief overall quality comment"
    )


class TranslationSegment(BaseModel):
    """A single source-target segment from an uploaded file."""

    id: int
    source_text: str
    target_text: str
    source_lang: str = ""
    target_lang: str = ""


class SegmentScore(BaseModel):
    """Computed score for a single segment."""

    segment_id: int
    word_count: int
    total_penalty: float
    annotations: list[ErrorAnnotation]


class DocumentScore(BaseModel):
    """Aggregated score for the entire document."""

    total_segments: int
    total_word_count: int
    total_penalty: float
    error_score: float  # penalty points per 1000 words
    error_score_pass_fail: str  # "Pass" or "Fail"
    critical_error_count: int
    critical_count_pass_fail: str  # "Pass" or "Fail"
    overall_pass_fail: str  # "Pass" or "Fail"
    quality_rating: int  # 1-5
    quality_rating_description: str
    error_type_counts: dict[str, int]  # error_type -> count
    severity_counts: dict[str, int]  # severity -> count
    # Detailed breakdown: error_type -> {severity -> count}
    error_type_severity_counts: dict[str, dict[str, int]]
    # Per error type penalty totals
    error_type_penalties: dict[str, float]
