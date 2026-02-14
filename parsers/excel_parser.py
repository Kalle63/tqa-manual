import pandas as pd

from models.data_models import TranslationSegment


def parse_excel(
    uploaded_file, source_lang: str = "", target_lang: str = ""
) -> list[TranslationSegment]:
    """
    Parse an Excel (.xlsx) file with three columns (by position):
      1. Segment number
      2. Source text (ST segment)
      3. Translated text (target segment)

    First row is treated as a header. Language pair is provided externally.
    Returns a list of TranslationSegment objects.
    """
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    if len(df.columns) < 3:
        raise ValueError(
            f"Excel file must have at least 3 columns (segment number, source, target). "
            f"Found {len(df.columns)} columns."
        )

    # Take first three columns by position
    cols = df.columns[:3]
    df = df[cols].copy()
    df.columns = ["segment_number", "source_text", "target_text"]

    # Drop rows where source or target is empty
    df = df.dropna(subset=["source_text", "target_text"])

    segments = []
    for _, row in df.iterrows():
        seg_num = row["segment_number"]
        seg_id = int(seg_num) if pd.notna(seg_num) else len(segments)

        segments.append(
            TranslationSegment(
                id=seg_id,
                source_text=str(row["source_text"]).strip(),
                target_text=str(row["target_text"]).strip(),
                source_lang=source_lang,
                target_lang=target_lang,
            )
        )

    return segments
