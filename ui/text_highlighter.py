"""Kohdetekstin näyttö korostuksineen ja maalauksen kopiointi leikepöydälle."""

import streamlit as st
import streamlit.components.v1 as components


# Severity-based highlight colors
SEVERITY_HIGHLIGHT_COLORS = {
    "Minor": "#a3d5ff",
    "Major": "#ffd699",
    "Critical": "#ff9999",
}


def _render_highlighted_html(target_text: str, existing_annotations: list) -> str:
    """Luo HTML-merkkijono korostetuista virheistä."""
    if not existing_annotations:
        return _escape_html(target_text)

    char_colors = [None] * len(target_text)
    for ann in existing_annotations:
        color = SEVERITY_HIGHLIGHT_COLORS.get(ann.severity, "#cccccc")
        idx = target_text.find(ann.span)
        if idx >= 0:
            for i in range(idx, min(idx + len(ann.span), len(target_text))):
                char_colors[i] = color

    result = []
    i = 0
    while i < len(target_text):
        if char_colors[i]:
            color = char_colors[i]
            j = i
            while j < len(target_text) and char_colors[j] == color:
                j += 1
            result.append(
                f'<mark style="background-color:{color};padding:2px 4px;'
                f'border-radius:3px;">'
                f'{_escape_html(target_text[i:j])}</mark>'
            )
            i = j
        else:
            j = i
            while j < len(target_text) and not char_colors[j]:
                j += 1
            result.append(_escape_html(target_text[i:j]))
            i = j

    return "".join(result)


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def render_text_highlighter(
    target_text: str,
    existing_annotations: list,
    key: str,
    **kwargs,
) -> None:
    """
    Renderoi kohdeteksti korostettuna.
    Maalattu teksti kopioituu automaattisesti leikepöydälle.
    """
    highlighted = _render_highlighted_html(target_text, existing_annotations)

    html_content = f"""
    <div id="target-container" style="
        font-size:1rem;line-height:1.8;padding:12px 16px;
        border:1px solid #ddd;border-radius:8px;background:#fafafa;
        min-height:50px;white-space:pre-wrap;word-wrap:break-word;
        cursor:text;user-select:text;-webkit-user-select:text;
    ">{highlighted}</div>
    <div id="sel-info" style="
        margin-top:6px;padding:6px 10px;font-size:0.85rem;
        color:#555;border-radius:4px;display:none;
        background:#e8f4fd;border:1px solid #b8daff;
    "></div>
    <script>
    (function() {{
        const container = document.getElementById('target-container');
        const info = document.getElementById('sel-info');

        container.addEventListener('mouseup', function() {{
            const selection = window.getSelection();
            const text = selection ? selection.toString().trim() : '';
            if (text.length > 0) {{
                navigator.clipboard.writeText(text).catch(function() {{}});
                info.style.display = 'block';
                info.innerHTML = '\\u2705 "<b>' + text.replace(/</g,'&lt;')
                    + '</b>" kopioitu leikepöydälle \\u2192 liitä Ctrl+V / Cmd+V';
            }}
        }});
    }})();
    </script>
    """

    lines = target_text.count("\n") + 1
    char_estimate = len(target_text) / 80
    est_lines = max(lines, int(char_estimate)) + 1
    height = max(80, min(est_lines * 32 + 60, 400))

    components.html(html_content, height=height, scrolling=True)
