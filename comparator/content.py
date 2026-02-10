"""Content comparison: text content diff recognizing {{Iterable}} variables."""

import re
from typing import List
from bs4 import BeautifulSoup, Tag, NavigableString
from config import ITERABLE_VAR_PATTERN


def _get_text_blocks(soup: BeautifulSoup) -> List[dict]:
    """Extract meaningful text blocks with their element context."""
    blocks = []
    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                               'td', 'th', 'li', 'a', 'span', 'div']):
        # Get direct text content (not children's text)
        text = tag.get_text(strip=True)
        if not text or len(text) < 2:
            continue

        classes = tag.get('class', [])
        if isinstance(classes, str):
            classes = classes.split()
        sig = tag.name + ('.' + '.'.join(sorted(classes)) if classes else '')

        blocks.append({
            'signature': sig,
            'text': text,
            'tag': tag.name,
        })

    return blocks


def _normalize_text(text: str) -> str:
    """Normalize text for comparison (collapse whitespace, lowercase)."""
    return re.sub(r'\s+', ' ', text).strip().lower()


def compare_content(reference_html: str, built_html: str) -> List[dict]:
    """Compare text content between reference and built email.

    Returns a list of difference dicts with keys:
        type: 'changed' | 'missing' | 'added' | 'unresolved_variable'
        element: element description
        reference_text: text in reference (or None)
        built_text: text in built (or None)
        details: human-readable explanation
    """
    ref_soup = BeautifulSoup(reference_html, 'html.parser')
    built_soup = BeautifulSoup(built_html, 'html.parser')

    ref_blocks = _get_text_blocks(ref_soup)
    built_blocks = _get_text_blocks(built_soup)

    diffs = []

    # Match blocks by signature
    from collections import defaultdict
    ref_by_sig = defaultdict(list)
    built_by_sig = defaultdict(list)

    for b in ref_blocks:
        ref_by_sig[b['signature']].append(b)
    for b in built_blocks:
        built_by_sig[b['signature']].append(b)

    # Compare matched elements
    for sig, ref_list in ref_by_sig.items():
        built_list = built_by_sig.get(sig, [])
        pairs = min(len(ref_list), len(built_list))

        for i in range(pairs):
            ref_text = ref_list[i]['text']
            built_text = built_list[i]['text']

            ref_norm = _normalize_text(ref_text)
            built_norm = _normalize_text(built_text)

            if ref_norm == built_norm:
                continue

            # Check if difference is just variable substitution
            ref_has_vars = bool(re.search(ITERABLE_VAR_PATTERN, ref_text))
            built_has_vars = bool(re.search(ITERABLE_VAR_PATTERN, built_text))

            if ref_has_vars and not built_has_vars:
                # Variables were substituted — this is expected
                # But check if any variables remain unresolved
                continue

            if built_has_vars:
                # Built email still has unresolved variables
                unresolved = re.findall(ITERABLE_VAR_PATTERN, built_text)
                for var in unresolved:
                    diffs.append({
                        'type': 'unresolved_variable',
                        'element': f"<{sig}> #{i+1}",
                        'reference_text': ref_text[:80],
                        'built_text': built_text[:80],
                        'details': f"Unresolved template variable: {var}",
                    })
                continue

            diffs.append({
                'type': 'changed',
                'element': f"<{sig}> #{i+1}",
                'reference_text': ref_text[:100],
                'built_text': built_text[:100],
                'details': "Text content differs",
            })

        # Missing text blocks
        if len(built_list) < len(ref_list):
            for j in range(len(built_list), len(ref_list)):
                diffs.append({
                    'type': 'missing',
                    'element': f"<{sig}> #{j+1}",
                    'reference_text': ref_list[j]['text'][:100],
                    'built_text': None,
                    'details': f"Text block removed from <{sig}>",
                })

        # Added text blocks
        if len(ref_list) < len(built_list):
            for j in range(len(ref_list), len(built_list)):
                diffs.append({
                    'type': 'added',
                    'element': f"<{sig}> #{j+1}",
                    'reference_text': None,
                    'built_text': built_list[j]['text'][:100],
                    'details': f"New text block added in <{sig}>",
                })

    # Check for unresolved variables anywhere in the built email
    all_built_text = built_soup.get_text()
    unresolved = re.findall(ITERABLE_VAR_PATTERN, all_built_text)
    seen = set()
    for var in unresolved:
        if var not in seen:
            seen.add(var)
            diffs.append({
                'type': 'unresolved_variable',
                'element': 'document',
                'reference_text': None,
                'built_text': var,
                'details': f"Unresolved template variable in built email: {var}",
            })

    return diffs
