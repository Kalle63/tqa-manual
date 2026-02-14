"""TQA Manual - Manuaalinen käännöslaadun arviointi."""

import streamlit as st

from ui.sidebar import render_sidebar
from ui.segment_table import render_segment_table
from ui.annotation_form import render_annotation_panel
from ui.dashboard import render_dashboard
from ui.export import render_export_button
from assessment.scoring import score_segment, score_document
from i18n.fi import FI


def main():
    st.set_page_config(
        page_title=FI["page_title"],
        layout="wide",
    )

    st.title(FI["page_title"])
    st.caption(FI["page_subtitle"])

    # Sivupalkki: lataus, kielet, tallennus/lataus
    render_sidebar()

    segments = st.session_state.get("segments")
    assessments = st.session_state.get("assessments")

    if not segments:
        st.markdown(f"### {FI['getting_started']}")
        st.markdown(FI["getting_started_steps"])
        return

    # Kaksi valilehtea
    tab_segments, tab_dashboard = st.tabs(
        [FI["tab_segments"], FI["tab_dashboard"]]
    )

    with tab_segments:
        # Segmenttitaulukko
        st.subheader(f"{len(segments)} {FI['segments_loaded']}")
        selected_idx = render_segment_table(segments, assessments)

        st.divider()

        # Virhemerkintapaneeli valitulle segmentille
        if selected_idx is not None:
            render_annotation_panel(
                seg_idx=selected_idx,
                segment=segments[selected_idx],
                assessment=assessments[selected_idx],
            )
        else:
            st.info(FI["select_segment"])

        # Pistelasku-painike
        st.divider()
        if st.button(FI["calculate_scores"], type="primary"):
            _recalculate_scores(segments, assessments)
            st.rerun()

    with tab_dashboard:
        if st.session_state.get("document_score"):
            render_dashboard()
            st.divider()
            render_export_button()
        else:
            st.info(FI["run_assessment_first"])


def _recalculate_scores(segments, assessments):
    """Laske pisteet nykyisten virhemerkintoen perusteella."""
    seg_scores = []
    for seg, assessment in zip(segments, assessments):
        seg_score = score_segment(
            segment_id=seg.id,
            target_text=seg.target_text,
            annotations=assessment.annotations,
        )
        seg_scores.append(seg_score)

    doc_score = score_document(seg_scores)
    st.session_state["segment_scores"] = seg_scores
    st.session_state["document_score"] = doc_score


if __name__ == "__main__":
    main()
