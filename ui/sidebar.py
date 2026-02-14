"""Sivupalkki: tiedoston lataus, kielivalinta, tallennus/lataus."""

import json

import streamlit as st

from parsers.excel_parser import parse_excel
from models.data_models import SegmentAssessment, TranslationSegment
from assessment.scoring import (
    ERROR_SCORE_THRESHOLD,
    CRITICAL_ERROR_MAX,
    QUALITY_RATING_THRESHOLDS,
)
from i18n.fi import FI


# Oletusasetukset (vastaavat scoring.py:n vakioita)
DEFAULT_SCORING_SETTINGS = {
    "rating_thresholds": [t[0] for t in QUALITY_RATING_THRESHOLDS],  # [5, 15, 25, 40]
    "pass_fail_threshold": ERROR_SCORE_THRESHOLD,  # 40
    "critical_error_max": CRITICAL_ERROR_MAX,  # 1
}


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

        # Pisteytysasetukset
        _render_scoring_settings()

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


def _get_scoring_settings() -> dict:
    """Palauta nykyiset pisteytysasetukset (tai oletukset)."""
    if "scoring_settings" not in st.session_state:
        st.session_state["scoring_settings"] = dict(DEFAULT_SCORING_SETTINGS)
    return st.session_state["scoring_settings"]


def _render_scoring_settings():
    """Pisteytysasetukset expanderissa."""
    # Jos edellisellä kierroksella painettiin "Palauta oletusasetukset",
    # aseta widgettien arvot ENNEN niiden luomista
    if st.session_state.pop("_reset_scoring", False):
        defaults = DEFAULT_SCORING_SETTINGS
        for rating, default_val in zip(
            [5, 4, 3, 2], defaults["rating_thresholds"]
        ):
            st.session_state[f"rating_thresh_{rating}"] = default_val
        st.session_state["pf_threshold"] = defaults["pass_fail_threshold"]
        st.session_state["crit_max"] = defaults["critical_error_max"]
        st.session_state["scoring_settings"] = dict(defaults)

    settings = _get_scoring_settings()
    rt = settings["rating_thresholds"]

    # Alusta widget-avaimet session stateen vain kerran (ei ristiriitaa value-parametrin kanssa)
    for rating, default_val in zip([5, 4, 3, 2], rt):
        if f"rating_thresh_{rating}" not in st.session_state:
            st.session_state[f"rating_thresh_{rating}"] = int(default_val)
    if "pf_threshold" not in st.session_state:
        st.session_state["pf_threshold"] = int(settings["pass_fail_threshold"])
    if "crit_max" not in st.session_state:
        st.session_state["crit_max"] = int(settings["critical_error_max"])

    with st.expander(f"⚙️ {FI['scoring_settings']}", expanded=False):
        # Arvosanarajat
        new_rt = []
        for i, (rating, _) in enumerate([(5, rt[0]), (4, rt[1]), (3, rt[2]), (2, rt[3])]):
            val = st.number_input(
                FI[f"rating_threshold_label_{rating}"],
                min_value=0,
                max_value=999,
                step=1,
                key=f"rating_thresh_{rating}",
            )
            new_rt.append(val)

        st.caption(FI["rating_1_info"])

        st.divider()

        # Hyväksymisraja
        pf_threshold = st.number_input(
            FI["pass_fail_threshold_label"],
            min_value=0,
            max_value=999,
            step=1,
            key="pf_threshold",
        )

        # Kriittisten virheiden enimmäismäärä
        crit_max = st.number_input(
            FI["critical_error_max_label"],
            min_value=0,
            max_value=99,
            step=1,
            key="crit_max",
        )

        # Päivitä session state
        st.session_state["scoring_settings"] = {
            "rating_thresholds": new_rt,
            "pass_fail_threshold": pf_threshold,
            "critical_error_max": crit_max,
        }

        st.divider()

        # Palauta oletukset — aseta lippu ja käynnistä uudelleen
        if st.button(FI["reset_defaults"], key="reset_scoring"):
            st.session_state["_reset_scoring"] = True
            st.rerun()


def _render_save_load():
    """Tallenna arviointi JSON:na ja lataa aiempi arviointi."""
    segments = st.session_state.get("segments")
    assessments = st.session_state.get("assessments")

    # Tallenna
    if segments and assessments:
        save_data = {
            "version": 2,
            "source_lang": st.session_state.get("source_lang", ""),
            "target_lang": st.session_state.get("target_lang", ""),
            "segments": [seg.model_dump() for seg in segments],
            "assessments": [asmt.model_dump() for asmt in assessments],
            "scoring_settings": _get_scoring_settings(),
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

        # Lataa pisteytysasetukset (yhteensopivuus vanhojen tiedostojen kanssa)
        loaded_settings = data.get("scoring_settings")
        if loaded_settings:
            st.session_state["scoring_settings"] = loaded_settings
            # Päivitä widgettien arvot
            rt = loaded_settings.get("rating_thresholds", DEFAULT_SCORING_SETTINGS["rating_thresholds"])
            for rating, val in zip([5, 4, 3, 2], rt):
                st.session_state[f"rating_thresh_{rating}"] = val
            st.session_state["pf_threshold"] = loaded_settings.get(
                "pass_fail_threshold", DEFAULT_SCORING_SETTINGS["pass_fail_threshold"]
            )
            st.session_state["crit_max"] = loaded_settings.get(
                "critical_error_max", DEFAULT_SCORING_SETTINGS["critical_error_max"]
            )

        st.success(FI["load_success"])
    except Exception as e:
        st.error(f"Virhe ladattaessa: {e}")
