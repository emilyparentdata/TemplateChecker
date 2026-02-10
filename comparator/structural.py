"""Structural comparison: DOM structure diff between reference and built email."""

from typing import List
from bs4 import BeautifulSoup, Tag


def _element_signature(tag: Tag) -> str:
    """Create a signature for an element: tag_name.class1.class2."""
    classes = tag.get('class', [])
    if isinstance(classes, str):
        classes = classes.split()
    cls = '.'.join(sorted(classes)) if classes else ''
    role = tag.get('role', '')
    sig = tag.name
    if cls:
        sig += '.' + cls
    if role:
        sig += f'[role={role}]'
    return sig


def _build_path(tag: Tag) -> str:
    """Build a CSS-like path to the element."""
    parts = []
    current = tag
    while current and current.name:
        parts.append(_element_signature(current))
        current = current.parent
    parts.reverse()
    return ' > '.join(parts[-4:])  # Last 4 levels for brevity


def _walk_elements(soup: BeautifulSoup) -> List[dict]:
    """Walk all elements and build a list of element info dicts."""
    elements = []
    for tag in soup.find_all(True):
        elements.append({
            'tag': tag.name,
            'signature': _element_signature(tag),
            'path': _build_path(tag),
            'classes': tag.get('class', []),
            'id': tag.get('id', ''),
        })
    return elements


def compare_structure(reference_html: str, built_html: str) -> List[dict]:
    """Compare DOM structure between reference and built email.

    Returns a list of difference dicts with keys:
        type: 'missing' | 'added' | 'reordered'
        element: description of the element
        details: human-readable explanation
    """
    ref_soup = BeautifulSoup(reference_html, 'html.parser')
    built_soup = BeautifulSoup(built_html, 'html.parser')

    ref_elements = _walk_elements(ref_soup)
    built_elements = _walk_elements(built_soup)

    ref_sigs = [e['signature'] for e in ref_elements]
    built_sigs = [e['signature'] for e in built_elements]

    # Count occurrences of each signature
    from collections import Counter
    ref_counts = Counter(ref_sigs)
    built_counts = Counter(built_sigs)

    diffs = []

    # Find missing elements (in reference but not in built)
    for sig, count in ref_counts.items():
        built_count = built_counts.get(sig, 0)
        if built_count < count:
            missing = count - built_count
            # Find the path from reference
            ref_el = next(e for e in ref_elements if e['signature'] == sig)
            diffs.append({
                'type': 'missing',
                'element': sig,
                'details': f"Missing {missing}x <{sig}> (was at: {ref_el['path']})",
            })

    # Find added elements (in built but not in reference)
    for sig, count in built_counts.items():
        ref_count = ref_counts.get(sig, 0)
        if ref_count < count:
            added = count - ref_count
            built_el = next(e for e in built_elements if e['signature'] == sig)
            diffs.append({
                'type': 'added',
                'element': sig,
                'details': f"Added {added}x <{sig}> (at: {built_el['path']})",
            })

    # Check for reordering of shared elements
    shared_ref = [s for s in ref_sigs if s in built_counts]
    shared_built = [s for s in built_sigs if s in ref_counts]

    # Simple reorder check: compare sequence of shared signatures
    if shared_ref and shared_built:
        # Deduplicate to check relative ordering
        seen_ref = []
        for s in shared_ref:
            if s not in seen_ref:
                seen_ref.append(s)
        seen_built = []
        for s in shared_built:
            if s not in seen_built:
                seen_built.append(s)

        # Find elements that changed position
        for i, sig in enumerate(seen_ref):
            if sig in seen_built:
                built_idx = seen_built.index(sig)
                if abs(i - built_idx) > 2:  # Allow minor shifts
                    diffs.append({
                        'type': 'reordered',
                        'element': sig,
                        'details': f"<{sig}> moved from position ~{i+1} to ~{built_idx+1}",
                    })

    return diffs
