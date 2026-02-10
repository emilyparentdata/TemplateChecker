"""Font compatibility rule: detect custom fonts without web-safe fallbacks."""

import re
from typing import List, Tuple
from bs4 import BeautifulSoup, Tag
from checker.models import Issue, FixApplied
from checker.rules.base import BaseRule
from config import WEB_SAFE_FALLBACKS, WEB_SAFE_FONTS


def parse_font_family(value: str) -> List[str]:
    """Parse a font-family CSS value into individual font names."""
    fonts = []
    for part in value.split(','):
        font = part.strip().strip("'\"").lower()
        if font:
            fonts.append(font)
    return fonts


def has_web_safe_fallback(fonts: List[str]) -> bool:
    """Check if the font list ends with a web-safe font."""
    if not fonts:
        return True
    for font in fonts[1:]:
        if font in WEB_SAFE_FONTS:
            return True
    return False


def build_fixed_font_family(original_value: str) -> str:
    """Add web-safe fallbacks to a font-family value if needed."""
    fonts = parse_font_family(original_value)
    if not fonts or has_web_safe_fallback(fonts):
        return original_value

    primary = fonts[0]
    fallback = WEB_SAFE_FALLBACKS.get(primary, "Arial, Helvetica, sans-serif")

    # Rebuild preserving the original first font's quoting
    parts = [p.strip() for p in original_value.split(',')]
    first_font = parts[0]
    # Add fallback fonts that aren't already present
    existing_lower = {f.strip().strip("'\"").lower() for f in parts}
    new_parts = [first_font]
    for fb in fallback.split(','):
        fb_clean = fb.strip().strip("'\"").lower()
        if fb_clean not in existing_lower:
            new_parts.append(fb.strip())
    return ', '.join(new_parts)


class FontRule(BaseRule):
    name = "fonts"
    description = "Custom font detection and fallback validation"

    def check(self, soup: BeautifulSoup, html: str) -> List[Issue]:
        issues = []

        # Check for Google Fonts link tags
        for link in soup.find_all('link', href=True):
            href = link['href']
            if 'fonts.googleapis.com' in href:
                issues.append(Issue(
                    rule=self.name,
                    severity='info',
                    message=f"Google Fonts link detected: {href}. "
                            "These won't load in many email clients (Gmail, Outlook).",
                    element=str(link)[:100],
                    can_fix=False,
                ))

        # Check for @font-face in style blocks
        for style in soup.find_all('style'):
            if style.string and '@font-face' in style.string:
                issues.append(Issue(
                    rule=self.name,
                    severity='info',
                    message="@font-face declaration found. Custom fonts won't "
                            "render in most email clients.",
                    element='<style> block',
                    can_fix=False,
                ))

        # Check inline font-family declarations for missing fallbacks
        for tag in soup.find_all(style=True):
            style_val = tag.get('style', '')
            match = re.search(r'font-family:\s*([^;]+)', style_val)
            if match:
                font_value = match.group(1).strip()
                fonts = parse_font_family(font_value)
                if fonts and not has_web_safe_fallback(fonts):
                    issues.append(Issue(
                        rule=self.name,
                        severity='warning',
                        message=f"Font '{fonts[0]}' has no web-safe fallback. "
                                "If the font fails to load, the browser default will be used.",
                        element=f"<{tag.name}> with font-family: {font_value}",
                        can_fix=True,
                    ))

        return issues

    def fix(self, soup: BeautifulSoup, html: str) -> Tuple[BeautifulSoup, str, List[FixApplied]]:
        fixes = []

        for tag in soup.find_all(style=True):
            style_val = tag.get('style', '')
            match = re.search(r'font-family:\s*([^;]+)', style_val)
            if match:
                font_value = match.group(1).strip()
                fonts = parse_font_family(font_value)
                if fonts and not has_web_safe_fallback(fonts):
                    fixed = build_fixed_font_family(font_value)
                    if fixed != font_value:
                        new_style = style_val.replace(font_value, fixed)
                        tag['style'] = new_style
                        fixes.append(FixApplied(
                            rule=self.name,
                            description=f"Added web-safe fallback to font-family",
                            before=f"font-family: {font_value}",
                            after=f"font-family: {fixed}",
                        ))

        if fixes:
            html = str(soup)
        return soup, html, fixes
