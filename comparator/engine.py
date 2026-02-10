"""Comparator engine: orchestrates all comparison modules."""

import re
from comparator.structural import compare_structure
from comparator.styles import compare_styles
from comparator.content import compare_content
from comparator.links import compare_links


def run_comparison(reference_html: str, built_html: str) -> dict:
    """Run all comparisons between reference template and built email.

    Returns a dict with keys: structure, styles, content, links.
    Each value is a list of difference dicts.
    """
    return {
        'structure': compare_structure(reference_html, built_html),
        'styles': compare_styles(reference_html, built_html),
        'content': compare_content(reference_html, built_html),
        'links': compare_links(reference_html, built_html),
    }


def total_differences(results: dict) -> int:
    """Count total number of differences across all categories."""
    return sum(len(v) for v in results.values())


# Keyword-to-relevance mapping for symptom diagnosis
SYMPTOM_KEYWORDS = {
    'font': {
        'properties': ['font-family', 'font-size', 'font-weight', 'font-style',
                        'letter-spacing', 'line-height'],
        'elements': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span'],
        'types': [],
        'categories': ['styles'],
    },
    'typeface': {
        'properties': ['font-family'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'text style': {
        'properties': ['font-family', 'font-size', 'font-weight', 'font-style',
                        'letter-spacing', 'line-height', 'text-decoration',
                        'text-transform'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'color': {
        'properties': ['color', 'background-color', 'background', 'opacity'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'colour': {
        'properties': ['color', 'background-color', 'background', 'opacity'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'dark': {
        'properties': ['color', 'background-color', 'background', 'opacity'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'light': {
        'properties': ['color', 'background-color', 'background', 'opacity'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'background': {
        'properties': ['background-color', 'background', 'background-image'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'spacing': {
        'properties': ['padding', 'margin', 'line-height', 'letter-spacing'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'padding': {
        'properties': ['padding', 'padding-top', 'padding-bottom',
                        'padding-left', 'padding-right'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'margin': {
        'properties': ['margin', 'margin-top', 'margin-bottom',
                        'margin-left', 'margin-right'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'gap': {
        'properties': ['padding', 'margin', 'gap'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'alignment': {
        'properties': ['text-align', 'vertical-align'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'image': {
        'properties': [],
        'elements': ['img'],
        'types': [],
        'categories': ['links', 'structure'],
    },
    'logo': {
        'properties': [],
        'elements': ['img'],
        'types': [],
        'categories': ['links', 'structure'],
    },
    'picture': {
        'properties': [],
        'elements': ['img'],
        'types': [],
        'categories': ['links', 'structure'],
    },
    'photo': {
        'properties': [],
        'elements': ['img'],
        'types': [],
        'categories': ['links', 'structure'],
    },
    'icon': {
        'properties': [],
        'elements': ['img'],
        'types': [],
        'categories': ['links', 'structure'],
    },
    'link': {
        'properties': [],
        'elements': ['a'],
        'types': [],
        'categories': ['links'],
    },
    'url': {
        'properties': [],
        'elements': ['a'],
        'types': [],
        'categories': ['links'],
    },
    'href': {
        'properties': [],
        'elements': ['a'],
        'types': [],
        'categories': ['links'],
    },
    'button': {
        'properties': [],
        'elements': ['a'],
        'types': [],
        'categories': ['links', 'styles'],
    },
    'click': {
        'properties': [],
        'elements': ['a'],
        'types': [],
        'categories': ['links'],
    },
    'missing': {
        'properties': [],
        'elements': [],
        'types': ['missing'],
        'categories': [],
    },
    'gone': {
        'properties': [],
        'elements': [],
        'types': ['missing'],
        'categories': [],
    },
    'disappeared': {
        'properties': [],
        'elements': [],
        'types': ['missing'],
        'categories': [],
    },
    'removed': {
        'properties': [],
        'elements': [],
        'types': ['missing'],
        'categories': [],
    },
    'extra': {
        'properties': [],
        'elements': [],
        'types': ['added'],
        'categories': [],
    },
    'added': {
        'properties': [],
        'elements': [],
        'types': ['added'],
        'categories': [],
    },
    'new': {
        'properties': [],
        'elements': [],
        'types': ['added'],
        'categories': [],
    },
    'unexpected': {
        'properties': [],
        'elements': [],
        'types': ['added'],
        'categories': [],
    },
    'moved': {
        'properties': [],
        'elements': [],
        'types': ['reordered'],
        'categories': [],
    },
    'order': {
        'properties': [],
        'elements': [],
        'types': ['reordered'],
        'categories': [],
    },
    'position': {
        'properties': [],
        'elements': [],
        'types': ['reordered'],
        'categories': [],
    },
    'shifted': {
        'properties': [],
        'elements': [],
        'types': ['reordered'],
        'categories': [],
    },
    'variable': {
        'properties': [],
        'elements': [],
        'types': ['unresolved_variable'],
        'categories': ['content'],
    },
    'merge tag': {
        'properties': [],
        'elements': [],
        'types': ['unresolved_variable'],
        'categories': ['content'],
    },
    'personalization': {
        'properties': [],
        'elements': [],
        'types': ['unresolved_variable'],
        'categories': ['content'],
    },
    '{{': {
        'properties': [],
        'elements': [],
        'types': ['unresolved_variable'],
        'categories': ['content'],
    },
    'size': {
        'properties': ['width', 'height', 'max-width', 'min-width',
                        'max-height', 'font-size'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'width': {
        'properties': ['width', 'max-width', 'min-width'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'height': {
        'properties': ['height', 'max-height', 'min-height'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'dimension': {
        'properties': ['width', 'height', 'max-width', 'font-size'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'big': {
        'properties': ['width', 'height', 'max-width', 'font-size'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'small': {
        'properties': ['width', 'height', 'max-width', 'font-size'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'border': {
        'properties': ['border', 'border-radius', 'border-top', 'border-bottom',
                        'border-left', 'border-right', 'border-color',
                        'border-width', 'border-style'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'outline': {
        'properties': ['border', 'outline'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'rounded': {
        'properties': ['border-radius'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'shadow': {
        'properties': ['box-shadow', 'text-shadow'],
        'elements': [],
        'types': [],
        'categories': ['styles'],
    },
    'layout': {
        'properties': [],
        'elements': ['table', 'tr', 'td', 'th', 'div'],
        'types': [],
        'categories': ['structure'],
    },
    'broken': {
        'properties': [],
        'elements': [],
        'types': [],
        'categories': ['structure'],
    },
    'structure': {
        'properties': [],
        'elements': [],
        'types': [],
        'categories': ['structure'],
    },
    'table': {
        'properties': [],
        'elements': ['table', 'tr', 'td', 'th'],
        'types': [],
        'categories': ['structure'],
    },
}


def _extract_diff_text(diff: dict) -> str:
    """Build a searchable text blob from all values in a diff dict."""
    parts = []
    for key, val in diff.items():
        if val is not None:
            parts.append(str(val).lower())
    return ' '.join(parts)


def _score_diff(diff: dict, category: str, matched_keywords: dict) -> tuple:
    """Score a single diff against the matched keyword signals.

    Returns (score, list_of_reasons).
    """
    score = 0
    reasons = []
    diff_text = _extract_diff_text(diff)
    diff_type = diff.get('type', '')
    diff_property = diff.get('property', '')
    diff_element = diff.get('element', '')

    for keyword, signals in matched_keywords.items():
        keyword_matched = False

        # Check property match (for style diffs)
        if diff_property and signals['properties']:
            for prop in signals['properties']:
                if prop in diff_property:
                    score += 3
                    reasons.append(f"Matches '{keyword}': {diff_property} property")
                    keyword_matched = True
                    break

        # Check element match
        if signals['elements'] and diff_element:
            element_lower = diff_element.lower()
            for elem in signals['elements']:
                if elem in element_lower:
                    score += 2
                    reasons.append(f"Matches '{keyword}': <{elem}> element")
                    keyword_matched = True
                    break

        # Check type match
        if signals['types'] and diff_type in signals['types']:
            score += 3
            reasons.append(f"Matches '{keyword}': {diff_type} diff type")
            keyword_matched = True

        # Check category match
        if signals['categories'] and category in signals['categories']:
            score += 1
            keyword_matched = True

        # Bonus: keyword appears directly in diff text
        if not keyword_matched and keyword in diff_text:
            score += 1
            reasons.append(f"Matches '{keyword}' in diff details")

    return score, reasons


def diagnose_issue(results: dict, symptom: str) -> list:
    """Filter and score diffs by relevance to the user's symptom description.

    Args:
        results: comparison results dict from run_comparison()
        symptom: free-text symptom description from user

    Returns:
        List of {category, diff, score, explanation} dicts sorted by score desc.
    """
    symptom_lower = symptom.lower().strip()
    if not symptom_lower:
        return []

    # Match symptom text against keyword map
    matched_keywords = {}
    for keyword, signals in SYMPTOM_KEYWORDS.items():
        if keyword in symptom_lower:
            matched_keywords[keyword] = signals

    if not matched_keywords:
        return []

    # Score every diff in every category
    scored = []
    for category, diffs in results.items():
        for diff in diffs:
            score, reasons = _score_diff(diff, category, matched_keywords)
            if score > 0:
                scored.append({
                    'category': category,
                    'diff': diff,
                    'score': score,
                    'explanation': '; '.join(reasons) if reasons else '',
                })

    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored
