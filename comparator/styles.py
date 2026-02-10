"""Style comparison: inline CSS property diff between matched elements."""

from typing import List
from bs4 import BeautifulSoup, Tag


def _parse_inline_style(style_str: str) -> dict:
    """Parse an inline style string into a property->value dict."""
    props = {}
    if not style_str:
        return props
    for decl in style_str.split(';'):
        decl = decl.strip()
        if ':' in decl:
            name, val = decl.split(':', 1)
            props[name.strip().lower()] = val.strip()
    return props


def _element_key(tag: Tag, index: int) -> str:
    """Create a key for matching elements between two DOMs."""
    classes = tag.get('class', [])
    if isinstance(classes, str):
        classes = classes.split()
    cls = '.'.join(sorted(classes)) if classes else ''
    return f"{tag.name}:{cls}:{index}"


def compare_styles(reference_html: str, built_html: str) -> List[dict]:
    """Compare inline CSS between reference and built email.

    Returns a list of difference dicts with keys:
        element: description of the element
        property: CSS property name
        type: 'changed' | 'missing' | 'added'
        reference_value: value in reference (or None)
        built_value: value in built (or None)
    """
    ref_soup = BeautifulSoup(reference_html, 'html.parser')
    built_soup = BeautifulSoup(built_html, 'html.parser')

    diffs = []

    # Build maps of elements by signature for matching
    def build_element_map(soup):
        from collections import defaultdict
        sig_map = defaultdict(list)
        for tag in soup.find_all(True):
            classes = tag.get('class', [])
            if isinstance(classes, str):
                classes = classes.split()
            sig = tag.name + ('.' + '.'.join(sorted(classes)) if classes else '')
            sig_map[sig].append(tag)
        return sig_map

    ref_map = build_element_map(ref_soup)
    built_map = build_element_map(built_soup)

    # Compare matched elements
    for sig, ref_tags in ref_map.items():
        built_tags = built_map.get(sig, [])
        pairs = min(len(ref_tags), len(built_tags))

        for i in range(pairs):
            ref_style = _parse_inline_style(ref_tags[i].get('style', ''))
            built_style = _parse_inline_style(built_tags[i].get('style', ''))

            if not ref_style and not built_style:
                continue

            # Find changed and missing properties
            for prop, ref_val in ref_style.items():
                built_val = built_style.get(prop)
                if built_val is None:
                    diffs.append({
                        'element': f"<{sig}> #{i+1}",
                        'property': prop,
                        'type': 'missing',
                        'reference_value': ref_val,
                        'built_value': None,
                    })
                elif ref_val != built_val:
                    diffs.append({
                        'element': f"<{sig}> #{i+1}",
                        'property': prop,
                        'type': 'changed',
                        'reference_value': ref_val,
                        'built_value': built_val,
                    })

            # Find added properties
            for prop, built_val in built_style.items():
                if prop not in ref_style:
                    diffs.append({
                        'element': f"<{sig}> #{i+1}",
                        'property': prop,
                        'type': 'added',
                        'reference_value': None,
                        'built_value': built_val,
                    })

    return diffs
