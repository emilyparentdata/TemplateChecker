"""Image rule: check for missing alt text, display:block, and dimensions."""

import re
from typing import List, Tuple
from bs4 import BeautifulSoup
from checker.models import Issue, FixApplied
from checker.rules.base import BaseRule


class ImageRule(BaseRule):
    name = "images"
    description = "Image alt text, display:block, and dimension checks"

    def check(self, soup: BeautifulSoup, html: str) -> List[Issue]:
        issues = []

        for img in soup.find_all('img'):
            src = img.get('src', '(no src)')
            short_src = src.split('/')[-1][:40] if src else '(no src)'

            # Missing alt
            if not img.has_attr('alt'):
                issues.append(Issue(
                    rule=self.name,
                    severity='warning',
                    message=f"Image missing alt attribute: {short_src}. "
                            "Screen readers and email clients that block images "
                            "will show nothing.",
                    element=f"<img src='{short_src}'>",
                    can_fix=True,
                ))

            # Missing display:block
            style = img.get('style', '')
            if 'display' not in style.lower() or 'block' not in style.lower():
                issues.append(Issue(
                    rule=self.name,
                    severity='info',
                    message=f"Image missing display:block: {short_src}. "
                            "Some email clients add extra spacing below images.",
                    element=f"<img src='{short_src}'>",
                    can_fix=True,
                ))

            # Missing width/height attributes
            if not img.has_attr('width') and not img.has_attr('height'):
                has_css_dims = bool(re.search(r'(?:width|height)\s*:', style))
                if not has_css_dims:
                    issues.append(Issue(
                        rule=self.name,
                        severity='info',
                        message=f"Image missing width/height: {short_src}. "
                                "Outlook needs explicit dimensions.",
                        element=f"<img src='{short_src}'>",
                        can_fix=False,
                    ))

        return issues

    def fix(self, soup: BeautifulSoup, html: str) -> Tuple[BeautifulSoup, str, List[FixApplied]]:
        fixes = []

        for img in soup.find_all('img'):
            src = img.get('src', '')
            short_src = src.split('/')[-1][:40] if src else '(no src)'

            # Add alt="" if missing
            if not img.has_attr('alt'):
                img['alt'] = ''
                fixes.append(FixApplied(
                    rule=self.name,
                    description="Added empty alt attribute",
                    before=f"<img src='{short_src}'> (no alt)",
                    after=f"<img src='{short_src}' alt=''>",
                ))

            # Add display:block if missing
            style = img.get('style', '')
            if 'display' not in style.lower() or 'block' not in style.lower():
                if style and not style.rstrip().endswith(';'):
                    style += '; '
                elif style:
                    style += ' '
                style += 'display: block;'
                img['style'] = style
                fixes.append(FixApplied(
                    rule=self.name,
                    description=f"Added display:block to image",
                    before=f"<img src='{short_src}'> (no display:block)",
                    after=f"Added display: block;",
                ))

        if fixes:
            html = str(soup)
        return soup, html, fixes
