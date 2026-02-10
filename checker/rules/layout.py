"""Layout rule: detect div-based layouts using flex/grid (report only)."""

import re
from typing import List, Tuple
from bs4 import BeautifulSoup
from checker.models import Issue, FixApplied
from checker.rules.base import BaseRule


class LayoutRule(BaseRule):
    name = "layout"
    description = "Div-based layout detection (flex/grid)"

    def check(self, soup: BeautifulSoup, html: str) -> List[Issue]:
        issues = []

        for tag in soup.find_all(style=True):
            style = tag.get('style', '').lower()
            if tag.name == 'table' or tag.name == 'td':
                continue

            if 'display: flex' in style or 'display:flex' in style:
                issues.append(Issue(
                    rule=self.name,
                    severity='error',
                    message=f"<{tag.name}> uses flexbox layout. This will break "
                            "in Gmail and Outlook. Use table-based layout instead.",
                    element=f"<{tag.name}>",
                    can_fix=False,
                ))
            elif 'display: grid' in style or 'display:grid' in style:
                issues.append(Issue(
                    rule=self.name,
                    severity='error',
                    message=f"<{tag.name}> uses CSS Grid layout. This will break "
                            "in Gmail and Outlook. Use table-based layout instead.",
                    element=f"<{tag.name}>",
                    can_fix=False,
                ))

        # Also check style blocks for class-based flex/grid
        for style_tag in soup.find_all('style'):
            css = style_tag.string or ''
            if re.search(r'display\s*:\s*flex', css):
                issues.append(Issue(
                    rule=self.name,
                    severity='warning',
                    message="Flexbox layout detected in <style> block. "
                            "This won't work in Gmail or Outlook.",
                    element='<style> block',
                    can_fix=False,
                ))
            if re.search(r'display\s*:\s*grid', css):
                issues.append(Issue(
                    rule=self.name,
                    severity='warning',
                    message="CSS Grid layout detected in <style> block. "
                            "This won't work in Gmail or Outlook.",
                    element='<style> block',
                    can_fix=False,
                ))

        return issues

    def fix(self, soup: BeautifulSoup, html: str) -> Tuple[BeautifulSoup, str, List[FixApplied]]:
        # Layout conversion is too risky to auto-fix
        return soup, html, []
