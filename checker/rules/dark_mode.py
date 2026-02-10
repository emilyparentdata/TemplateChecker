"""Dark mode rule: detect prefers-color-scheme usage (report only)."""

import re
from typing import List, Tuple
from bs4 import BeautifulSoup
from checker.models import Issue, FixApplied
from checker.rules.base import BaseRule


class DarkModeRule(BaseRule):
    name = "dark_mode"
    description = "Dark mode (prefers-color-scheme) detection"

    def check(self, soup: BeautifulSoup, html: str) -> List[Issue]:
        issues = []

        for i, style in enumerate(soup.find_all('style'), 1):
            css = style.string or ''
            if 'prefers-color-scheme' in css:
                matches = re.findall(
                    r'@media\s*\([^)]*prefers-color-scheme\s*:\s*(\w+)[^)]*\)',
                    css
                )
                scheme = matches[0] if matches else 'dark'
                issues.append(Issue(
                    rule=self.name,
                    severity='info',
                    message=f"prefers-color-scheme: {scheme} detected in style "
                            f"block #{i}. Gmail does not support this media query. "
                            "Dark mode adaptations won't apply in Gmail.",
                    element=f"<style> block #{i}",
                    can_fix=False,
                ))

        # Check for meta color-scheme
        for meta in soup.find_all('meta', attrs={'name': 'color-scheme'}):
            issues.append(Issue(
                rule=self.name,
                severity='info',
                message=f"meta color-scheme detected: {meta.get('content', '')}. "
                        "Limited email client support.",
                element='<meta name="color-scheme">',
                can_fix=False,
            ))

        return issues

    def fix(self, soup: BeautifulSoup, html: str) -> Tuple[BeautifulSoup, str, List[FixApplied]]:
        # Dark mode is report-only
        return soup, html, []
