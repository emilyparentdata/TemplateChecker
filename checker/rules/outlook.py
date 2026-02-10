"""Outlook rule: detect missing MSO properties and VML fallbacks."""

import re
from typing import List, Tuple
from bs4 import BeautifulSoup
from checker.models import Issue, FixApplied
from checker.rules.base import BaseRule


class OutlookRule(BaseRule):
    name = "outlook"
    description = "Outlook MSO properties and VML fallback detection"

    def check(self, soup: BeautifulSoup, html: str) -> List[Issue]:
        issues = []

        # Check tables for MSO properties
        for table in soup.find_all('table'):
            style = table.get('style', '')
            has_mso_lspace = 'mso-table-lspace' in style
            has_mso_rspace = 'mso-table-rspace' in style

            if not has_mso_lspace or not has_mso_rspace:
                # Check if set via class in <style> block (already handled)
                classes = table.get('class', [])
                if isinstance(classes, str):
                    classes = classes.split()
                # Only flag if no mso properties at all
                if not has_mso_lspace and not has_mso_rspace:
                    issues.append(Issue(
                        rule=self.name,
                        severity='info',
                        message="Table missing mso-table-lspace and mso-table-rspace. "
                                "Outlook may add default cell spacing.",
                        element=f"<table> (classes: {' '.join(classes) if classes else 'none'})",
                        can_fix=True,
                    ))

        # Check for background-image without VML fallback
        for tag in soup.find_all(style=True):
            style = tag.get('style', '')
            if 'background-image' in style.lower() or 'background:' in style.lower():
                bg_match = re.search(r'(?:background-image|background)\s*:[^;]*url\s*\(', style)
                if bg_match:
                    # Check if there's a VML fallback nearby
                    parent_html = str(tag.parent) if tag.parent else ''
                    has_vml = 'v:fill' in parent_html.lower() or 'v:rect' in parent_html.lower()
                    if not has_vml:
                        # Check the full HTML for VML near this element
                        has_vml = '<!--[if gte mso 9]>' in html and 'v:' in html
                        issues.append(Issue(
                            rule=self.name,
                            severity='warning',
                            message="CSS background-image detected without VML fallback. "
                                    "Background images won't render in Outlook (Windows).",
                            element=f"<{tag.name}> with background-image",
                            can_fix=False,
                        ))

        return issues

    def fix(self, soup: BeautifulSoup, html: str) -> Tuple[BeautifulSoup, str, List[FixApplied]]:
        fixes = []

        for table in soup.find_all('table'):
            style = table.get('style', '')
            additions = []

            if 'mso-table-lspace' not in style:
                additions.append('mso-table-lspace: 0pt')
            if 'mso-table-rspace' not in style:
                additions.append('mso-table-rspace: 0pt')

            if additions:
                if style and not style.rstrip().endswith(';'):
                    style += '; '
                elif style:
                    style += ' '
                style += '; '.join(additions) + ';'
                table['style'] = style
                fixes.append(FixApplied(
                    rule=self.name,
                    description="Added MSO table spacing properties",
                    before="<table> missing MSO properties",
                    after=f"Added: {'; '.join(additions)}",
                ))

        if fixes:
            html = str(soup)
        return soup, html, fixes
