"""CSS support rule: detect unsupported CSS properties per email client."""

import re
from typing import List, Tuple
from bs4 import BeautifulSoup
from checker.models import Issue, FixApplied
from checker.rules.base import BaseRule
from config import UNSUPPORTED_CSS


def check_style_value(style_str: str) -> List[dict]:
    """Check a style string for unsupported CSS properties."""
    found = []
    props = [p.strip() for p in style_str.split(';') if p.strip()]

    for prop in props:
        if ':' not in prop:
            continue
        name, value = prop.split(':', 1)
        name = name.strip().lower()
        value = value.strip().lower()

        # Check property name
        if name in UNSUPPORTED_CSS:
            info = UNSUPPORTED_CSS[name]
            safe_values = info.get('safe_values', set())
            if safe_values and value in safe_values:
                continue
            found.append({
                'property': name,
                'value': value,
                'full': prop.strip(),
                'info': info,
            })

        # Check property: value combinations (e.g., "display: flex")
        combo = f"{name}: {value}"
        for unsup_key, unsup_info in UNSUPPORTED_CSS.items():
            if ': ' in unsup_key:
                unsup_name, unsup_val = unsup_key.split(': ', 1)
                if name == unsup_name and value == unsup_val:
                    found.append({
                        'property': name,
                        'value': value,
                        'full': prop.strip(),
                        'info': unsup_info,
                    })

    return found


# Properties that are safe to remove without breaking layout
REMOVABLE_PROPERTIES = {'white-space-collapse', 'opacity'}


class CSSSupportRule(BaseRule):
    name = "css_support"
    description = "Unsupported CSS properties per email client"

    def check(self, soup: BeautifulSoup, html: str) -> List[Issue]:
        issues = []

        for tag in soup.find_all(style=True):
            style_val = tag.get('style', '')
            problems = check_style_value(style_val)
            for p in problems:
                info = p['info']
                issues.append(Issue(
                    rule=self.name,
                    severity=info['severity'],
                    message=f"'{p['full']}' — {info['description']}. "
                            f"Not supported in: {', '.join(info['clients'])}.",
                    element=f"<{tag.name}> style",
                    can_fix=p['property'] in REMOVABLE_PROPERTIES,
                ))

        return issues

    def fix(self, soup: BeautifulSoup, html: str) -> Tuple[BeautifulSoup, str, List[FixApplied]]:
        fixes = []

        for tag in soup.find_all(style=True):
            style_val = tag.get('style', '')
            problems = check_style_value(style_val)
            removable = [p for p in problems if p['property'] in REMOVABLE_PROPERTIES]

            if not removable:
                continue

            new_style = style_val
            for p in removable:
                # Remove the problematic property
                pattern = re.compile(
                    r'\s*' + re.escape(p['property']) + r'\s*:\s*[^;]*;?\s*',
                    re.IGNORECASE
                )
                new_style = pattern.sub('', new_style)
                fixes.append(FixApplied(
                    rule=self.name,
                    description=f"Removed unsupported CSS property '{p['property']}'",
                    before=p['full'],
                    after="(removed)",
                ))

            new_style = new_style.strip()
            if new_style.endswith(';'):
                pass
            elif new_style and not new_style.endswith(';'):
                new_style += ';'

            tag['style'] = new_style if new_style else None
            if tag.get('style') is None and tag.has_attr('style'):
                del tag['style']

        if fixes:
            html = str(soup)
        return soup, html, fixes
