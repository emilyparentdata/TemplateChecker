"""Style block size rule: detect style blocks exceeding Gmail's 8,192 char limit."""

from typing import List, Tuple
from bs4 import BeautifulSoup, Tag
from checker.models import Issue, FixApplied
from checker.rules.base import BaseRule
from config import GMAIL_STYLE_BLOCK_LIMIT


class StyleBlockRule(BaseRule):
    name = "style_block"
    description = "Gmail 8,192-character style block limit"

    def check(self, soup: BeautifulSoup, html: str) -> List[Issue]:
        issues = []

        for i, style in enumerate(soup.find_all('style'), 1):
            content = style.string or ''
            length = len(content)
            if length > GMAIL_STYLE_BLOCK_LIMIT:
                issues.append(Issue(
                    rule=self.name,
                    severity='error',
                    message=f"Style block #{i} is {length:,} characters "
                            f"(limit: {GMAIL_STYLE_BLOCK_LIMIT:,}). "
                            "Gmail will ignore this entire block.",
                    element=f"<style> block #{i}",
                    can_fix=True,
                ))

        return issues

    def fix(self, soup: BeautifulSoup, html: str) -> Tuple[BeautifulSoup, str, List[FixApplied]]:
        fixes = []

        for style in soup.find_all('style'):
            # Skip Outlook conditional comments
            if style.parent and hasattr(style.parent, 'name') and style.parent.name is None:
                continue

            content = style.string or ''
            if len(content) <= GMAIL_STYLE_BLOCK_LIMIT:
                continue

            # Split CSS into rule blocks
            rules = []
            current = []
            brace_depth = 0
            for char in content:
                current.append(char)
                if char == '{':
                    brace_depth += 1
                elif char == '}':
                    brace_depth -= 1
                    if brace_depth == 0:
                        rules.append(''.join(current))
                        current = []

            if current:
                leftover = ''.join(current).strip()
                if leftover:
                    rules.append(leftover)

            if not rules:
                continue

            # Split rules into chunks under the limit
            chunks = []
            current_chunk = []
            current_size = 0

            for rule in rules:
                rule_size = len(rule)
                if current_size + rule_size > GMAIL_STYLE_BLOCK_LIMIT and current_chunk:
                    chunks.append(''.join(current_chunk))
                    current_chunk = [rule]
                    current_size = rule_size
                else:
                    current_chunk.append(rule)
                    current_size += rule_size

            if current_chunk:
                chunks.append(''.join(current_chunk))

            if len(chunks) <= 1:
                continue

            # Replace original style tag with multiple
            style_type = style.get('type', 'text/css')
            first = True
            for chunk in chunks:
                if first:
                    style.string = chunk
                    first = False
                else:
                    new_style = soup.new_tag('style', type=style_type)
                    new_style.string = chunk
                    style.insert_after(new_style)

            fixes.append(FixApplied(
                rule=self.name,
                description=f"Split oversized style block into {len(chunks)} blocks",
                before=f"{len(content):,} characters in 1 block",
                after=f"Split into {len(chunks)} blocks, each under {GMAIL_STYLE_BLOCK_LIMIT:,} chars",
            ))

        if fixes:
            html = str(soup)
        return soup, html, fixes
