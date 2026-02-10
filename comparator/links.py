"""Link comparison: href and src attribute diff."""

from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def _get_links(soup: BeautifulSoup) -> List[dict]:
    """Extract all href and src values with context."""
    links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)[:50]
        links.append({
            'type': 'href',
            'url': href,
            'element': f"<a> '{text}'",
            'text': text,
        })

    for img in soup.find_all('img', src=True):
        src = img['src']
        alt = img.get('alt', '')[:50]
        links.append({
            'type': 'src',
            'url': src,
            'element': f"<img alt='{alt}'>",
            'text': alt,
        })

    # Also check link tags (stylesheets, etc.)
    for link in soup.find_all('link', href=True):
        links.append({
            'type': 'link_href',
            'url': link['href'],
            'element': f"<link rel='{link.get('rel', [''])[0]}'>",
            'text': '',
        })

    return links


def compare_links(reference_html: str, built_html: str) -> List[dict]:
    """Compare links between reference and built email.

    Returns a list of difference dicts with keys:
        type: 'missing' | 'added' | 'changed'
        element: element description
        reference_url: URL in reference (or None)
        built_url: URL in built (or None)
        details: human-readable explanation
    """
    ref_soup = BeautifulSoup(reference_html, 'html.parser')
    built_soup = BeautifulSoup(built_html, 'html.parser')

    ref_links = _get_links(ref_soup)
    built_links = _get_links(built_soup)

    diffs = []

    # Match links by element text/alt and type
    ref_by_key = {}
    for i, link in enumerate(ref_links):
        key = (link['type'], link['text'], i)
        ref_by_key[key] = link

    built_by_key = {}
    for i, link in enumerate(built_links):
        key = (link['type'], link['text'], i)
        built_by_key[key] = link

    # Also do positional matching for same-type links
    ref_by_type = {}
    built_by_type = {}
    for link in ref_links:
        ref_by_type.setdefault(link['type'], []).append(link)
    for link in built_links:
        built_by_type.setdefault(link['type'], []).append(link)

    for link_type in set(list(ref_by_type.keys()) + list(built_by_type.keys())):
        ref_list = ref_by_type.get(link_type, [])
        built_list = built_by_type.get(link_type, [])

        pairs = min(len(ref_list), len(built_list))
        for i in range(pairs):
            ref_url = ref_list[i]['url']
            built_url = built_list[i]['url']

            if ref_url != built_url:
                diffs.append({
                    'type': 'changed',
                    'element': ref_list[i]['element'],
                    'reference_url': ref_url,
                    'built_url': built_url,
                    'details': f"URL changed in {ref_list[i]['element']}",
                })

        # Missing links
        for i in range(pairs, len(ref_list)):
            diffs.append({
                'type': 'missing',
                'element': ref_list[i]['element'],
                'reference_url': ref_list[i]['url'],
                'built_url': None,
                'details': f"Link removed: {ref_list[i]['element']}",
            })

        # Added links
        for i in range(pairs, len(built_list)):
            diffs.append({
                'type': 'added',
                'element': built_list[i]['element'],
                'reference_url': None,
                'built_url': built_list[i]['url'],
                'details': f"Link added: {built_list[i]['element']}",
            })

    return diffs
