"""Taulukkonäkymä segmenteista, rivin valinta."""

import streamlit as st

from models.data_models import TranslationSegment, SegmentAssessment
from i18n.fi import FI


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_segment_table(
    segments: list[TranslationSegment],
    assessments: list[SegmentAssessment],
) -> int | None:
    """
    Renderoi segmenttitaulukko ja segmentin valinta.
    Palauttaa valitun rivin indeksin tai None.
    """
    # HTML-taulukko word wrap -tuella
    header = (
        f"<tr>"
        f"<th style='padding:8px 12px;text-align:left;border-bottom:2px solid #ddd;"
        f"background:#f8f9fa;white-space:nowrap;'>{FI['segment_col']}</th>"
        f"<th style='padding:8px 12px;text-align:left;border-bottom:2px solid #ddd;"
        f"background:#f8f9fa;'>{FI['source_col']}</th>"
        f"<th style='padding:8px 12px;text-align:left;border-bottom:2px solid #ddd;"
        f"background:#f8f9fa;'>{FI['target_col']}</th>"
        f"<th style='padding:8px 12px;text-align:center;border-bottom:2px solid #ddd;"
        f"background:#f8f9fa;white-space:nowrap;'>{FI['errors_col']}</th>"
        f"</tr>"
    )

    rows_html = []
    for i, seg in enumerate(segments):
        error_count = len(assessments[i].annotations) if i < len(assessments) else 0
        error_badge = (
            f"<span style='background:#ff4b4b;color:white;padding:2px 8px;"
            f"border-radius:10px;font-size:0.85em;'>{error_count}</span>"
            if error_count > 0
            else f"<span style='color:#999;'>0</span>"
        )
        bg = "#ffffff" if i % 2 == 0 else "#f9f9fb"
        rows_html.append(
            f"<tr style='background:{bg};'>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #eee;"
            f"vertical-align:top;white-space:nowrap;font-weight:600;'>"
            f"{_escape_html(str(seg.id))}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #eee;"
            f"vertical-align:top;word-wrap:break-word;'>"
            f"{_escape_html(seg.source_text)}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #eee;"
            f"vertical-align:top;word-wrap:break-word;'>"
            f"{_escape_html(seg.target_text)}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #eee;"
            f"vertical-align:top;text-align:center;'>"
            f"{error_badge}</td>"
            f"</tr>"
        )

    table_html = (
        f"<div style='max-height:500px;overflow-y:auto;border:1px solid #ddd;"
        f"border-radius:8px;'>"
        f"<table style='width:100%;border-collapse:collapse;font-size:0.9rem;"
        f"table-layout:fixed;'>"
        f"<colgroup>"
        f"<col style='width:80px;'>"
        f"<col style='width:45%;'>"
        f"<col style='width:45%;'>"
        f"<col style='width:70px;'>"
        f"</colgroup>"
        f"<thead>{header}</thead>"
        f"<tbody>{''.join(rows_html)}</tbody>"
        f"</table></div>"
    )

    st.html(table_html)

    # Segmentin valinta selectboxilla
    selected = st.selectbox(
        FI.get("select_segment_label", "Valitse segmentti"),
        options=range(len(segments)),
        format_func=lambda i: f"{segments[i].id} — {segments[i].target_text}",
        key="segment_selector",
        index=None,
        placeholder=FI.get("select_segment_placeholder", "Valitse segmentti..."),
    )

    return selected
