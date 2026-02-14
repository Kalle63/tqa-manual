"""Sivupalkki: tiedoston lataus, kielivalinta, tallennus/lataus."""

import json

import streamlit as st

from parsers.excel_parser import parse_excel
from models.data_models import SegmentAssessment, TranslationSegment
from i18n.fi import FI


SUPPORTED_LANGUAGES = [
    "englanti",
    "suomi",
    "ruotsi",
    "saksa",
    "ranska",
    "espanja",
    "italia",
    "portugali",
    "hollanti",
    "puola",
    "tshekki",
    "japani",
    "kiina (yksinkertaistettu)",
    "kiina (perinteinen)",
    "korea",
    "venäjä",
    "arabia",
    "hindi",
    "muu",
]


def render_sidebar():
    """Renderoi sivupalkki."""
    with st.sidebar:
        st.title(FI["sidebar_title"])

        # Kielivalinta
        source_lang = st.selectbox(
            FI["source_lang"], SUPPORTED_LANGUAGES, index=0, key="src_lang"
        )
        target_lang = st.selectbox(
            FI["target_lang"], SUPPORTED_LANGUAGES, index=1, key="tgt_lang"
        )
        st.session_state["source_lang"] = source_lang
        st.session_state["target_lang"] = target_lang

        st.divider()

        # Tiedoston lataus
        uploaded_file = st.file_uploader(
            FI["upload_label"],
            type=["xlsx"],
            help=FI["upload_help"],
            key="file_uploader",
        )

        if uploaded_file is not None:
            current_file = st.session_state.get("_uploaded_filename")
            if current_file != uploaded_file.name:
                _handle_upload(uploaded_file, source_lang, target_lang)
                st.session_state["_uploaded_filename"] = uploaded_file.name

        st.divider()

        # Tallennus ja lataus
        _render_save_load()


def _handle_upload(uploaded_file, source_lang: str, target_lang: str):
    """Käsittele ladattu Excel-tiedosto."""
    try:
        segments = parse_excel(uploaded_file, source_lang, target_lang)
        st.session_state["segments"] = segments
        # Luo tyhjat arvioinnit jokaiselle segmentille
        st.session_state["assessments"] = [
            SegmentAssessment(annotations=[], overall_comment="")
            for _ in segments
        ]
        st.session_state["segment_scores"] = None
        st.session_state["document_score"] = None
        st.success(f"{len(segments)} {FI['segments_loaded']}")
    except ValueError as e:
        st.error(f"Virhe: {e}")
    except Exception as e:
        st.error(f"Odottamaton virhe: {e}")


def _render_save_load():
    """Tallenna arviointi JSON:na ja lataa aiempi arviointi."""
    segments = st.session_state.get("segments")
    assessments = st.session_state.get("assessments")

    # Tallenna
    if segments and assessments:
        save_data = {
            "version": 1,
            "source_lang": st.session_state.get("source_lang", ""),
            "target_lang": st.session_state.get("target_lang", ""),
            "segments": [seg.model_dump() for seg in segments],
            "assessments": [asmt.model_dump() for asmt in assessments],
        }
        st.download_button(
            label=FI["save_session"],
            data=json.dumps(save_data, ensure_ascii=False, indent=2),
            file_name="tqa_arviointi.json",
            mime="application/json",
            help=FI["save_help"],
        )

    st.divider()

    # Lataa
    loaded_file = st.file_uploader(
        FI["load_file_label"],
        type=["json"],
        help=FI["load_help"],
        key="load_json_uploader",
    )

    if loaded_file is not None:
        current_loaded = st.session_state.get("_loaded_filename")
        if current_loaded != loaded_file.name:
            _handle_load(loaded_file)
            st.session_state["_loaded_filename"] = loaded_file.name


def _handle_load(json_file):
    """Lataa tallennettu arviointi JSON-tiedostosta."""
    try:
        data = json.load(json_file)
        segments = [TranslationSegment(**s) for s in data["segments"]]
        assessments = [SegmentAssessment(**a) for a in data["assessments"]]
        st.session_state["segments"] = segments
        st.session_state["assessments"] = assessments
        st.session_state["segment_scores"] = None
        st.session_state["document_score"] = None
        st.success(FI["load_success"])
    except Exception as e:
        st.error(f"Virhe ladattaessa: {e}")
