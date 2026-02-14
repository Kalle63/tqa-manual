from models.data_models import (
    ERROR_TYPES,
    SEVERITY_LEVELS,
    SEVERITY_PENALTIES,
    ErrorAnnotation,
    SegmentScore,
    DocumentScore,
)

# Scoring thresholds
ERROR_SCORE_THRESHOLD = 40  # Score <= 40 = Pass
CRITICAL_ERROR_MAX = 1  # More than 1 critical error = Fail

# Quality Rating thresholds (error score per 1000 words)
QUALITY_RATING_THRESHOLDS = [
    (5, 5, "Functional"),
    (15, 4, "Minor deficiencies"),
    (25, 3, "Isolated significant deficiencies"),
    (40, 2, "Serious deficiencies"),
]
# Anything above 40 = Rating 1


def count_words(text: str) -> int:
    """Count words in text by splitting on whitespace."""
    return len(text.split())


def calculate_annotation_penalty(annotation: ErrorAnnotation) -> float:
    """Calculate penalty points for a single annotation."""
    return SEVERITY_PENALTIES.get(annotation.severity, 0)


def score_segment(
    segment_id: int,
    target_text: str,
    annotations: list[ErrorAnnotation],
) -> SegmentScore:
    """Calculate the penalty total for a single segment."""
    word_count = max(count_words(target_text), 1)
    total_penalty = sum(calculate_annotation_penalty(a) for a in annotations)

    return SegmentScore(
        segment_id=segment_id,
        word_count=word_count,
        total_penalty=total_penalty,
        annotations=annotations,
    )


def get_quality_rating(error_score: float) -> tuple[int, str]:
    """
    Determine quality rating (1-5) from error score (per 1000 words).

    Returns (rating, description).
    """
    for threshold, rating, description in QUALITY_RATING_THRESHOLDS:
        if error_score <= threshold:
            return rating, description
    return 1, "Very serious deficiencies"


def score_document(segment_scores: list[SegmentScore]) -> DocumentScore:
    """
    Calculate the overall document score.

    Error Score = (Total Penalty Points / Word Count) * 1000
    Pass/Fail: Error Score <= 40 AND critical errors <= 1
    """
    total_word_count = sum(s.word_count for s in segment_scores)
    total_penalty = sum(s.total_penalty for s in segment_scores)

    if total_word_count == 0:
        error_score = 0.0
    else:
        error_score = (total_penalty / total_word_count) * 1000

    # Count critical errors
    critical_error_count = 0
    for seg in segment_scores:
        for ann in seg.annotations:
            if ann.severity == "Critical":
                critical_error_count += 1

    # Pass/Fail
    error_score_pass = error_score <= ERROR_SCORE_THRESHOLD
    critical_count_pass = critical_error_count <= CRITICAL_ERROR_MAX
    overall_pass = error_score_pass and critical_count_pass

    # Quality rating
    quality_rating, rating_description = get_quality_rating(error_score)

    # Error type counts
    error_type_counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}
    error_type_severity_counts: dict[str, dict[str, int]] = {
        et: {s: 0 for s in SEVERITY_LEVELS} for et in ERROR_TYPES
    }
    error_type_penalties: dict[str, float] = {et: 0.0 for et in ERROR_TYPES}

    for seg in segment_scores:
        for ann in seg.annotations:
            # Overall counts
            error_type_counts[ann.error_type] = (
                error_type_counts.get(ann.error_type, 0) + 1
            )
            severity_counts[ann.severity] = (
                severity_counts.get(ann.severity, 0) + 1
            )
            # Detailed breakdown
            if ann.error_type in error_type_severity_counts:
                if ann.severity in error_type_severity_counts[ann.error_type]:
                    error_type_severity_counts[ann.error_type][ann.severity] += 1
            if ann.error_type in error_type_penalties:
                error_type_penalties[ann.error_type] += calculate_annotation_penalty(
                    ann
                )

    return DocumentScore(
        total_segments=len(segment_scores),
        total_word_count=total_word_count,
        total_penalty=round(total_penalty, 2),
        error_score=round(error_score, 2),
        error_score_pass_fail="Pass" if error_score_pass else "Fail",
        critical_error_count=critical_error_count,
        critical_count_pass_fail="Pass" if critical_count_pass else "Fail",
        overall_pass_fail="Pass" if overall_pass else "Fail",
        quality_rating=quality_rating,
        quality_rating_description=rating_description,
        error_type_counts=error_type_counts,
        severity_counts=severity_counts,
        error_type_severity_counts=error_type_severity_counts,
        error_type_penalties=error_type_penalties,
    )
