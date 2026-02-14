"""Virhemerkintäpaneeli: tekstin maalaus + lomake + virhelista."""

import streamlit as st

from models.data_models import (
    ERROR_TYPES,
    SEVERITY_LEVELS,
    DEFAULT_SEVERITIES,
    ErrorAnnotation,
    SegmentAssessment,
    TranslationSegment,
)
from ui.text_highlighter import render_text_highlighter
from i18n.fi import FI

SEVERITY_COLORS_DISPLAY = {
    "Critical": "red",
    "Major": "orange",
    "Minor": "blue",
}


def render_annotation_panel(
    seg_idx: int,
    segment: TranslationSegment,
    assessment: SegmentAssessment,
):
    """Renderoi virhemerkintäpaneeli valitulle segmentille."""

    st.subheader(FI["annotate_header"].format(seg_id=segment.id))

    # Lähde ja kohde rinnakkain
    col_src, col_tgt = st.columns(2)
    with col_src:
        st.markdown(f"**{FI['source_label']}:**")
        st.text(segment.source_text)
    with col_tgt:
        st.markdown(f"**{FI['target_label']}:**")
        st.caption(FI["highlight_instruction"])
        try:
            render_text_highlighter(
                target_text=segment.target_text,
                existing_annotations=assessment.annotations,
                key=f"highlighter_{seg_idx}",
                span_input_label=FI["error_span"],
            )
        except Exception as e:
            st.warning(f"Maalauskomponentti ei käytettävissä: {e}")
            st.text(segment.target_text)

    st.divider()

    # Nykyiset virheet
    _render_existing_annotations(seg_idx, assessment)

    st.divider()

    # Uuden virheen lisäyslomake
    _render_add_form(seg_idx)

    # Yleiskommentti
    comment = st.text_area(
        FI["overall_comment"],
        value=assessment.overall_comment,
        key=f"comment_{seg_idx}",
    )
    if comment != assessment.overall_comment:
        st.session_state["assessments"][seg_idx].overall_comment = comment


def _render_existing_annotations(seg_idx: int, assessment: SegmentAssessment):
    """Näytä nykyiset virheet muokkaus- ja poistopainikkeilla."""
    if not assessment.annotations:
        st.success(FI["no_errors"])
        return

    # Käännostaulukot
    fi_to_en_type = {
        FI["error_type_names"].get(et, et): et for et in ERROR_TYPES
    }
    fi_to_en_sev = {
        FI["severity_names"].get(s, s): s for s in SEVERITY_LEVELS
    }
    fi_error_labels = list(fi_to_en_type.keys())
    fi_severity_labels = list(fi_to_en_sev.keys())

    # Tarkista, onko muokkauslomake auki jollekin virheelle
    editing_key = f"_editing_{seg_idx}"
    editing_idx = st.session_state.get(editing_key)

    st.markdown(f"**{FI['errors_found']}:**")
    for j, ann in enumerate(assessment.annotations):

        # Jos tämä virhe on muokkaustilassa, näytä lomake
        if editing_idx == j:
            _render_edit_form(seg_idx, j, ann, fi_to_en_type, fi_to_en_sev,
                              fi_error_labels, fi_severity_labels)
            continue

        color = SEVERITY_COLORS_DISPLAY.get(ann.severity, "gray")
        fi_type = FI["error_type_names"].get(ann.error_type, ann.error_type)
        fi_sev = FI["severity_names"].get(ann.severity, ann.severity)

        cols = st.columns([2, 2, 1, 2, 0.5, 0.5])
        with cols[0]:
            st.markdown(f"**{fi_type}**")
        with cols[1]:
            st.markdown(f'"{ann.span}"')
        with cols[2]:
            st.markdown(f":{color}[{fi_sev}]")
        with cols[3]:
            st.caption(ann.explanation)
        with cols[4]:
            if st.button(FI["edit"], key=f"edit_{seg_idx}_{j}"):
                st.session_state[editing_key] = j
                st.rerun()
        with cols[5]:
            if st.button(FI["delete"], key=f"del_{seg_idx}_{j}"):
                # Jos muokataan poistettavaa tai sitä myöhempää, nollaa muokkaustila
                if editing_idx is not None and editing_idx >= j:
                    st.session_state.pop(editing_key, None)
                st.session_state["assessments"][seg_idx].annotations.pop(j)
                st.rerun()


def _render_edit_form(seg_idx, ann_idx, ann, fi_to_en_type, fi_to_en_sev,
                      fi_error_labels, fi_severity_labels):
    """Muokkauslomake yksittäiselle virheelle."""
    editing_key = f"_editing_{seg_idx}"

    st.markdown("---")

    # Virhetyyppi — valitaan nykyinen arvo oletukseksi
    current_fi_type = FI["error_type_names"].get(ann.error_type, ann.error_type)
    type_index = fi_error_labels.index(current_fi_type) if current_fi_type in fi_error_labels else 0
    selected_fi_type = st.selectbox(
        FI["error_type"],
        fi_error_labels,
        index=type_index,
        key=f"edit_type_{seg_idx}_{ann_idx}",
    )
    new_error_type = fi_to_en_type[selected_fi_type]

    # Vakavuus
    current_fi_sev = FI["severity_names"].get(ann.severity, ann.severity)
    sev_index = fi_severity_labels.index(current_fi_sev) if current_fi_sev in fi_severity_labels else 0
    selected_fi_sev = st.selectbox(
        FI["severity"],
        fi_severity_labels,
        index=sev_index,
        key=f"edit_sev_{seg_idx}_{ann_idx}",
    )
    new_severity = fi_to_en_sev[selected_fi_sev]

    # Virhejakso
    new_span = st.text_input(
        FI["error_span"],
        value=ann.span,
        key=f"edit_span_{seg_idx}_{ann_idx}",
    )

    # Selitys
    new_explanation = st.text_input(
        FI["explanation"],
        value=ann.explanation,
        key=f"edit_expl_{seg_idx}_{ann_idx}",
    )

    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button(FI["save_edit"], key=f"save_edit_{seg_idx}_{ann_idx}", type="primary"):
            if new_span and new_explanation:
                st.session_state["assessments"][seg_idx].annotations[ann_idx] = ErrorAnnotation(
                    error_type=new_error_type,
                    severity=new_severity,
                    span=new_span,
                    explanation=new_explanation,
                )
                st.session_state.pop(editing_key, None)
                st.rerun()
            else:
                st.warning(FI["fill_required"])
    with col_cancel:
        if st.button(FI["cancel_edit"], key=f"cancel_edit_{seg_idx}_{ann_idx}"):
            st.session_state.pop(editing_key, None)
            st.rerun()

    st.markdown("---")


def _render_add_form(seg_idx: int):
    """Lomake uuden virheen lisäämiseksi."""

    # Jos edellisellä kierroksella lisättiin virhe, tyhjennä kentät
    # (tämä suoritetaan ENNEN widgettien luomista)
    if st.session_state.pop(f"_clear_form_{seg_idx}", False):
        st.session_state[f"add_span_{seg_idx}"] = ""
        st.session_state[f"add_expl_{seg_idx}"] = ""

    st.markdown(f"**{FI['add_error']}**")

    # Virhetyyppi
    fi_to_en_type = {
        FI["error_type_names"].get(et, et): et for et in ERROR_TYPES
    }
    fi_error_labels = list(fi_to_en_type.keys())
    selected_fi_type = st.selectbox(
        FI["error_type"],
        fi_error_labels,
        key=f"add_type_{seg_idx}",
    )
    error_type = fi_to_en_type[selected_fi_type]

    # Päivitä vakavuus automaattisesti kun virhetyyppi vaihtuu
    prev_type_key = f"_prev_type_{seg_idx}"
    if st.session_state.get(prev_type_key) != error_type:
        default_sev = DEFAULT_SEVERITIES.get(error_type, "Major")
        default_fi_sev = FI["severity_names"].get(default_sev, default_sev)
        st.session_state[f"add_sev_{seg_idx}"] = default_fi_sev
        st.session_state[prev_type_key] = error_type

    # Vakavuus
    fi_to_en_sev = {
        FI["severity_names"].get(s, s): s for s in SEVERITY_LEVELS
    }
    fi_severity_labels = list(fi_to_en_sev.keys())
    selected_fi_sev = st.selectbox(
        FI["severity"],
        fi_severity_labels,
        key=f"add_sev_{seg_idx}",
    )
    severity = fi_to_en_sev[selected_fi_sev]

    # Virhejakso
    span = st.text_input(
        FI["error_span"],
        key=f"add_span_{seg_idx}",
    )

    explanation = st.text_input(
        FI["explanation"],
        key=f"add_expl_{seg_idx}",
    )

    if st.button(FI["add_error"], key=f"add_btn_{seg_idx}", type="primary"):
        if span and explanation:
            new_ann = ErrorAnnotation(
                error_type=error_type,
                severity=severity,
                span=span,
                explanation=explanation,
            )
            st.session_state["assessments"][seg_idx].annotations.append(new_ann)
            # Merkitse tyhjennys seuraavalle kierrokselle
            st.session_state[f"_clear_form_{seg_idx}"] = True
            st.rerun()
        else:
            st.warning(FI["fill_required"])
