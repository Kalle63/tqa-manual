"""CSV-vienti suomeksi."""

import csv
import io

import streamlit as st

from models.data_models import SEVERITY_PENALTIES
from i18n.fi import FI


def render_export_button():
    """Renderoi lataa CSV -painike."""
    segments = st.session_state.get("segments")
    assessments = st.session_state.get("assessments")
    seg_scores = st.session_state.get("segment_scores")
    doc_score = st.session_state.get("document_score")

    if not segments or not assessments or not seg_scores:
        return

    csv_data = _generate_export_csv(segments, assessments, seg_scores, doc_score)

    st.download_button(
        label=FI["export_csv"],
        data=csv_data,
        file_name="tqa_tulokset.csv",
        mime="text/csv",
    )

    if doc_score:
        pf = FI["pass"] if doc_score.overall_pass_fail == "Pass" else FI["fail"]
        rating_info = FI["rating_descriptions"].get(doc_score.quality_rating, ("", ""))
        st.caption(
            f"{FI['error_score']}: {doc_score.error_score:.2f} | "
            f"{FI['quality_rating']}: {doc_score.quality_rating}/5 ({rating_info[0]}) | "
            f"{pf}"
        )


def _generate_export_csv(segments, assessments, seg_scores, doc_score) -> str:
    """Luo CSV-merkkijono: virherivit + kokonaistulokset."""
    output = io.StringIO()
    writer = csv.writer(output)

    # ── Osa 1: Virhekohtaiset rivit ──
    writer.writerow(
        [
            "Segmentti",
            "Lähdeteksti",
            "Kohdeteksti",
            "Lähdekieli",
            "Kohdekieli",
            "Virhetyyppi",
            "Vakavuusaste",
            "Virhejakso",
            "Selitys",
            "Pisteet",
            "Segmentin sanamäärä",
            "Segmentin virhepistesumma",
            "Yleiskommentti",
        ]
    )

    for seg, assessment, score in zip(segments, assessments, seg_scores):
        comment = assessment.overall_comment or ""
        if assessment.annotations:
            for i, ann in enumerate(assessment.annotations):
                penalty = SEVERITY_PENALTIES.get(ann.severity, 0)
                writer.writerow(
                    [
                        seg.id,
                        seg.source_text,
                        seg.target_text,
                        seg.source_lang,
                        seg.target_lang,
                        ann.error_type,
                        ann.severity,
                        ann.span,
                        ann.explanation,
                        penalty,
                        score.word_count,
                        score.total_penalty,
                        comment if i == 0 else "",
                    ]
                )
        else:
            writer.writerow(
                [
                    seg.id,
                    seg.source_text,
                    seg.target_text,
                    seg.source_lang,
                    seg.target_lang,
                    "",
                    "",
                    "",
                    "",
                    0,
                    score.word_count,
                    score.total_penalty,
                    comment,
                ]
            )

    # ── Osa 2: Kokonaistulokset ──
    if doc_score:
        writer.writerow([])
        writer.writerow(["KOKONAISTULOKSET"])
        writer.writerow([])

        pf_fi = "Hyväksytty" if doc_score.overall_pass_fail == "Pass" else "Hylätty"
        es_pf = "Hyväksytty" if doc_score.error_score_pass_fail == "Pass" else "Hylätty"
        cr_pf = "Hyväksytty" if doc_score.critical_count_pass_fail == "Pass" else "Hylätty"
        rating_info = FI["rating_descriptions"].get(
            doc_score.quality_rating, ("", "")
        )

        writer.writerow(["Segmenttejä yhteensä", doc_score.total_segments])
        writer.writerow(["Sanamäärä yhteensä", doc_score.total_word_count])
        writer.writerow(["Virhepistesumma", doc_score.total_penalty])
        writer.writerow([])
        writer.writerow(["Virhepisteet / 1000 sanaa", f"{doc_score.error_score:.2f}"])
        writer.writerow(["Virhepisteiden raja-arvo", "≤ 40"])
        writer.writerow(["Virhepisteet", es_pf])
        writer.writerow([])
        writer.writerow(["Kriittiset virheet", doc_score.critical_error_count])
        writer.writerow(["Kriittisten virheiden raja-arvo", "≤ 1"])
        writer.writerow(["Kriittiset virheet", cr_pf])
        writer.writerow([])
        writer.writerow(["Kokonaistulos", pf_fi])
        writer.writerow(
            ["Laatuarvosana", f"{doc_score.quality_rating}/5 — {rating_info[0]}"]
        )
        writer.writerow(["Kuvaus", rating_info[1]])

        # Virheet tyypeittäin
        writer.writerow([])
        writer.writerow(["VIRHEET TYYPEITTÄIN"])
        writer.writerow(["Virhetyyppi", "Lukumäärä", "Virhepistesumma"])
        for et, count in doc_score.error_type_counts.items():
            fi_name = FI["error_type_names"].get(et, et)
            penalty = doc_score.error_type_penalties.get(et, 0)
            writer.writerow([fi_name, count, penalty])

        # Virheet vakavuusasteittain
        writer.writerow([])
        writer.writerow(["VIRHEET VAKAVUUSASTEITTAIN"])
        writer.writerow(["Vakavuusaste", "Lukumäärä"])
        for sev, count in doc_score.severity_counts.items():
            fi_name = FI["severity_names"].get(sev, sev)
            writer.writerow([fi_name, count])

    return output.getvalue()
