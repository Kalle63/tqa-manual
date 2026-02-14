"""Pisteytyslomake ja yhteenvetonakyma suomeksi."""

import streamlit as st
import plotly.express as px
import pandas as pd

from models.data_models import (
    ERROR_TYPES,
    ERROR_TYPE_NUMBERS,
    SEVERITY_LEVELS,
    DocumentScore,
    SegmentScore,
)
from i18n.fi import FI


def render_dashboard():
    """Renderoi yhteenvetonakyma pisteytyslomakkeineen."""
    doc_score: DocumentScore | None = st.session_state.get("document_score")
    seg_scores: list[SegmentScore] | None = st.session_state.get("segment_scores")

    if not doc_score or not seg_scores:
        st.info(FI["run_assessment_first"])
        return

    _render_scorecard_header(doc_score)
    st.divider()
    _render_error_breakdown_table(doc_score)
    st.divider()
    _render_charts(doc_score)
    st.divider()
    _render_segment_table(seg_scores)


def _render_scorecard_header(doc_score: DocumentScore):
    """Paametriikat."""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(FI["error_score"], f"{doc_score.error_score:.2f}")
    with col2:
        st.metric(
            FI["quality_rating"],
            f"{doc_score.quality_rating}/5",
            help=doc_score.quality_rating_description,
        )
    with col3:
        pf = FI["pass"] if doc_score.overall_pass_fail == "Pass" else FI["fail"]
        st.metric(FI["overall"], pf)
    with col4:
        st.metric(FI["word_count"], doc_score.total_word_count)
    with col5:
        total_errors = sum(doc_score.error_type_counts.values())
        st.metric(FI["total_errors"], total_errors)

    # Hyvaksytty/hylatty -tiedot
    es_pf = FI["pass"] if doc_score.error_score_pass_fail == "Pass" else FI["fail"]
    cc_pf = FI["pass"] if doc_score.critical_count_pass_fail == "Pass" else FI["fail"]
    st.markdown(
        f"**{FI['error_score']}:** {es_pf} "
        f"({FI['error_score_threshold']}) &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"**{FI['critical_count']}:** {doc_score.critical_error_count} "
        f"({cc_pf}, {FI['critical_max']})"
    )

    # Laatuarvosanan kuvaus
    rating_info = FI["rating_descriptions"].get(doc_score.quality_rating)
    if rating_info:
        desc, action = rating_info
        st.info(f"**{FI['quality_rating']} {doc_score.quality_rating} - {desc}:** {action}")


def _render_error_breakdown_table(doc_score: DocumentScore):
    """Virhepisteytyslomake taulukkomuodossa."""
    st.subheader(FI["error_scorecard"])

    fi_minor = FI["severity_names"]["Minor"]
    fi_major = FI["severity_names"]["Major"]
    fi_critical = FI["severity_names"]["Critical"]

    rows = []
    for error_type in ERROR_TYPES:
        et_num = ERROR_TYPE_NUMBERS[error_type]
        severity_counts = doc_score.error_type_severity_counts.get(
            error_type, {s: 0 for s in SEVERITY_LEVELS}
        )
        total_count = sum(severity_counts.values())
        penalty_total = doc_score.error_type_penalties.get(error_type, 0)
        fi_type = FI["error_type_names"].get(error_type, error_type)

        rows.append(
            {
                "#": et_num,
                FI["error_type"]: fi_type,
                FI["count"]: total_count,
                f"{fi_minor} (x1)": severity_counts.get("Minor", 0) or "",
                f"{fi_major} (x5)": severity_counts.get("Major", 0) or "",
                f"{fi_critical} (x10)": severity_counts.get("Critical", 0) or "",
                FI["penalty"]: penalty_total if penalty_total > 0 else "",
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown(
        f"**{FI['total_penalty_points']}:** {doc_score.total_penalty} "
        f"&nbsp;&nbsp;|&nbsp;&nbsp; "
        f"**{FI['error_score_per_1000']}:** {doc_score.error_score:.2f}"
    )


def _render_charts(doc_score: DocumentScore):
    """Virhejakaumakaaviot."""
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader(FI["errors_by_type"])
        if doc_score.error_type_counts:
            # Kayta suomenkielisia nimia kaavioissa
            fi_names = [
                FI["error_type_names"].get(et, et)
                for et in doc_score.error_type_counts.keys()
            ]
            fig_type = px.bar(
                x=fi_names,
                y=list(doc_score.error_type_counts.values()),
                title=FI["errors_by_type"],
                labels={"x": FI["error_type"], "y": FI["count"]},
            )
            fig_type.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_type, use_container_width=True)
        else:
            st.success(FI["no_errors_found"])

    with chart_col2:
        st.subheader(FI["errors_by_severity"])
        if doc_score.severity_counts:
            severity_order = ["Critical", "Major", "Minor"]
            severity_colors = {
                "Critical": "#e74c3c",
                "Major": "#f39c12",
                "Minor": "#3498db",
            }
            ordered = [s for s in severity_order if s in doc_score.severity_counts]
            fi_ordered = [FI["severity_names"].get(s, s) for s in ordered]
            fig_sev = px.bar(
                x=fi_ordered,
                y=[doc_score.severity_counts[s] for s in ordered],
                color=fi_ordered,
                color_discrete_map={
                    FI["severity_names"].get(s, s): c
                    for s, c in severity_colors.items()
                },
                title=FI["errors_by_severity"],
                labels={"x": FI["severity"], "y": FI["count"]},
            )
            fig_sev.update_layout(showlegend=False)
            st.plotly_chart(fig_sev, use_container_width=True)
        else:
            st.success(FI["no_errors_found"])


def _render_segment_table(seg_scores: list[SegmentScore]):
    """Segmenttikohtainen taulukko."""
    st.subheader(FI["per_segment_details"])

    assessments = st.session_state.get("assessments", [])

    table_data = []
    for i, s in enumerate(seg_scores):
        comment = ""
        if i < len(assessments) and assessments[i].overall_comment:
            comment = assessments[i].overall_comment
        table_data.append(
            {
                FI["segment"]: s.segment_id,
                FI["words"]: s.word_count,
                FI["errors"]: len(s.annotations),
                FI["penalty"]: s.total_penalty,
                FI["overall_comment"]: comment,
            }
        )
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
