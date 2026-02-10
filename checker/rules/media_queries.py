"""Media query rule: detect conflicts with Outlook hacks in same style block."""

import re
from typing import List, Tuple
from bs4 import BeautifulSoup, NavigableString
from checker.models import Issue, FixApplied
from checker.rules.base import BaseRule


class MediaQueryRule(BaseRule):
    name = "media_queries"
    description = "Media query and Outlook hack conflict detection"

    def _has_outlook_hacks(self, css: str) -> bool:
        """Check if CSS contains Outlook-specific hacks."""
        patterns = [
            r'mso-',
            r'\.ExternalClass',
            r'#outlook',
            r'\*\s*\{[^}]*-ms-text-size-adjust',
        ]
        for pattern in patterns:
            if re.search(pattern, css):
                return True
        return False

    def _has_media_queries(self, css: str) -> bool:
        return bool(re.search(r'@media\b', css))

    def _extract_media_queries(self, css: str) -> tuple:
        """Split CSS into media queries and non-media-query parts."""
        non_mq = []
        mq = []
        # Track position through the CSS
        i = 0
        while i < len(css):
            mq_match = re.search(r'@media\b[^{]*\{', css[i:])
            if not mq_match:
                non_mq.append(css[i:])
                break

            # Everything before this @media is non-MQ
            non_mq.append(css[i:i + mq_match.start()])

            # Find the matching closing brace
            start = i + mq_match.start()
            brace_start = i + mq_match.end()
            depth = 1
            j = brace_start
            while j < len(css) and depth > 0:
                if css[j] == '{':
                    depth += 1
                elif css[j] == '}':
                    depth -= 1
                j += 1

            mq.append(css[start:j])
            i = j

        return ''.join(non_mq), '\n'.join(mq)

    def check(self, soup: BeautifulSoup, html: str) -> List[Issue]:
        issues = []

        for i, style in enumerate(soup.find_all('style'), 1):
            css = style.string or ''
            # Skip Outlook conditional blocks
            prev = style.previous_sibling
            if prev and isinstance(prev, NavigableString) and '[if' in str(prev):
                continue

            has_mq = self._has_media_queries(css)
            has_outlook = self._has_outlook_hacks(css)

            if has_mq and has_outlook:
                issues.append(Issue(
                    rule=self.name,
                    severity='warning',
                    message=f"Style block #{i} contains both media queries and "
                            "Outlook hacks (mso-*, .ExternalClass). Gmail mobile "
                            "may strip the entire block.",
                    element=f"<style> block #{i}",
                    can_fix=True,
                ))

        return issues

    def fix(self, soup: BeautifulSoup, html: str) -> Tuple[BeautifulSoup, str, List[FixApplied]]:
        fixes = []

        for style in soup.find_all('style'):
            css = style.string or ''
            prev = style.previous_sibling
            if prev and isinstance(prev, NavigableString) and '[if' in str(prev):
                continue

            has_mq = self._has_media_queries(css)
            has_outlook = self._has_outlook_hacks(css)

            if not (has_mq and has_outlook):
                continue

            non_mq, mq_css = self._extract_media_queries(css)
            if not mq_css.strip():
                continue

            # Keep non-MQ rules in original block
            style.string = non_mq.strip()

            # Create new style block for media queries
            new_style = soup.new_tag('style', type='text/css')
            new_style.string = '\n' + mq_css.strip() + '\n'
            style.insert_after(new_style)

            fixes.append(FixApplied(
                rule=self.name,
                description="Separated media queries from Outlook hacks",
                before="Media queries + Outlook hacks in same <style> block",
                after="Split into separate <style> blocks",
            ))

        if fixes:
            html = str(soup)
        return soup, html, fixes
