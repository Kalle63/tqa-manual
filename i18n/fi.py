"""Suomenkieliset UI-tekstit TQA Manual -sovellukselle."""

FI = {
    # Sivu
    "page_title": "TQA - Manuaalinen laadunarviointi",
    "page_subtitle": "ISO 5060 -mukainen virhepisteytyslomake",
    # Sivupalkki
    "sidebar_title": "Asetukset",
    "upload_label": "Lataa käännöstiedosto",
    "upload_help": "Excel-tiedosto (.xlsx): segmenttinumero, lähdeteksti, kohdeteksti",
    "source_lang": "Lähdekieli",
    "target_lang": "Kohdekieli",
    "save_session": "Tallenna arviointi",
    "load_session": "Lataa aiempi arviointi",
    "save_success": "Arviointi tallennettu!",
    "load_success": "Arviointi ladattu!",
    "save_help": "Tallentaa arvioinnin JSON-muodossa jatkamista varten",
    "load_help": "Lataa aiemmin tallennettu arviointi (.json)",
    "load_file_label": "Lataa arviointi (.json)",
    # Segmenttitaulukko
    "segments_loaded": "segmenttiä ladattu",
    "segment_col": "Segmentti",
    "source_col": "Lähdeteksti",
    "target_col": "Kohdeteksti",
    "errors_col": "Virheet",
    "select_segment": "Valitse segmentti alla olevasta valikosta.",
    "select_segment_label": "Valitse segmentti",
    "select_segment_placeholder": "Valitse segmentti...",
    # Virhemerkintä
    "annotate_header": "Segmentin {seg_id} virhearviointi",
    "source_label": "Lähde",
    "target_label": "Kohde",
    "highlight_instruction": "Maalaa virheellinen teksti hiirellä — se kopioituu leikepöydälle. Liitä Ctrl+V / Cmd+V.",
    "selected_text": "Valittu teksti",
    "error_type": "Virhetyyppi",
    "severity": "Vakavuusaste",
    "error_span": "Virheellinen tekstijakso",
    "explanation": "Selitys",
    "add_error": "Lisää virhe",
    "delete": "Poista",
    "no_errors": "Ei virheitä.",
    "errors_found": "Löydetyt virheet",
    "fill_required": "Täytä virhejakso ja selitys.",
    "overall_comment": "Yleiskommentti",
    # Virhetyyppien suomenkieliset nimet
    "error_type_names": {
        "Punctuation": "Välimerkit",
        "Grammar": "Kielioppi",
        "Spelling": "Oikeinkirjoitus",
        "Terminology": "Terminologia",
        "Style": "Tyyli",
        "Unidiomatic": "Epäidiomaattinen",
        "Untranslated": "Kääntämätön",
        "Major Mistranslation": "Merkittävä käännösvirhe",
        "Critical Mistranslation": "Kriittinen käännösvirhe",
        "Omission": "Puuttuva sisältö",
        "Numerical Error": "Numerovirhe",
    },
    # Vakavuusasteiden suomenkieliset nimet
    "severity_names": {
        "Minor": "Vähäinen",
        "Major": "Merkittävä",
        "Critical": "Kriittinen",
    },
    # Dashboard
    "dashboard_title": "Pisteytyslomake",
    "error_score": "Virhepisteet",
    "quality_rating": "Laatuarvosana",
    "overall": "Kokonaistulos",
    "word_count": "Sanamäärä",
    "total_errors": "Virheet yhteensä",
    "pass": "Hyväksytty",
    "fail": "Hylätty",
    "error_score_threshold": "raja-arvo: ≤ 40",
    "critical_count": "Kriittiset virheet",
    "critical_max": "max: 1",
    "error_scorecard": "Virhepisteytyslomake",
    "count": "Lukumäärä",
    "penalty": "Pisteet",
    "total_penalty_points": "Rangaistuspisteet yhteensä",
    "error_score_per_1000": "Virhepisteet / 1000 sanaa",
    "errors_by_type": "Virheet tyypeittäin",
    "errors_by_severity": "Virheet vakavuusasteittain",
    "per_segment_details": "Segmenttikohtaiset tiedot",
    "segment": "Segmentti",
    "words": "Sanat",
    "errors": "Virheet",
    "no_errors_found": "Virheitä ei löytynyt!",
    "run_assessment_first": "Tee arviointi ja napsauta 'Laske pisteet' nähdäksesi yhteenvedon.",
    # Laatuarvosanojen kuvaukset
    "rating_descriptions": {
        5: ("Toimiva", "Ei toimenpiteitä. Valmis julkaistavaksi."),
        4: ("Pieniä puutteita", "Kevyt oikoluku riittää."),
        3: ("Yksittäisiä merkittäviä puutteita", "Vaatii editointia, mutta pelastettavissa."),
        2: ("Vakavia puutteita", "Raskas editointi tai osittainen uudelleenkääntäminen."),
        1: ("Erittäin vakavia puutteita", "Hylätty. Uudelleenkääntäminen vaaditaan."),
    },
    # Vienti
    "export_csv": "Lataa tulokset CSV-tiedostona",
    # Aloitus
    "getting_started": "Aloitus",
    "getting_started_steps": (
        "1. Valitse lähde- ja kohdekieli sivupalkissa.\n"
        "2. Lataa Excel-tiedosto (.xlsx): segmenttinumero, lähdeteksti, kohdeteksti.\n"
        "3. Valitse segmentti valikosta ja aloita virhearviointi.\n"
        "4. Tallenna arviointi JSON-tiedostona milloin tahansa."
    ),
    # Välilehdet
    "tab_segments": "Segmentit",
    "tab_dashboard": "Yhteenveto",
    # Painikkeet
    "calculate_scores": "Laske pisteet",
}
