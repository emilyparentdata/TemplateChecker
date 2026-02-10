"""Inline CSS rule: detect critical styles only in <style> blocks (stripped by Gmail)."""

import re
from typing import List, Tuple
from bs4 import BeautifulSoup
from checker.models import Issue, FixApplied
from checker.rules.base import BaseRule

# Properties considered critical for email rendering
CRITICAL_INLINE_PROPS = {
    'font-family', 'font-size', 'color', 'background-color',
    'text-align', 'line-height', 'padding', 'margin',
    'width', 'height', 'border',
}


class InlineCSSRule(BaseRule):
    name = "inline_css"
    description = "CSS inlining completeness"

    def _get_class_styles(self, soup: BeautifulSoup) -> dict:
        """Extract class-based styles from <style> blocks."""
        class_styles = {}
        for style_tag in soup.find_all('style'):
            css = style_tag.string or ''
            # Skip Outlook conditional blocks
            if '<!--[if' in str(style_tag.parent or ''):
                continue
            # Simple regex to find class selectors and their properties
            pattern = re.compile(r'\.([a-zA-Z_][\w-]*)\s*\{([^}]+)\}')
            for match in pattern.finditer(css):
                cls = match.group(1)
                props = match.group(2).strip()
                class_styles[cls] = props
        return class_styles

    def check(self, soup: BeautifulSoup, html: str) -> List[Issue]:
        issues = []
        class_styles = self._get_class_styles(soup)

        if not class_styles:
            return issues

        # Find elements using classes that define critical properties
        for cls, props in class_styles.items():
            has_critical = False
            for prop in CRITICAL_INLINE_PROPS:
                if prop in props:
                    has_critical = True
                    break

            if not has_critical:
                continue

            # Check if elements with this class have inline equivalents
            elements = soup.find_all(class_=lambda c: c and cls in c.split())
            for el in elements:
                inline = el.get('style', '')
                missing = []
                for prop in CRITICAL_INLINE_PROPS:
                    if prop in props and prop not in inline:
                        missing.append(prop)

                if missing:
                    issues.append(Issue(
                        rule=self.name,
                        severity='warning',
                        message=f"Class '.{cls}' defines {', '.join(missing[:3])} "
                                "in <style> block only. Gmail strips <style> blocks — "
                                "these styles need inline equivalents.",
                        element=f"<{el.name} class='{cls}'>",
                        can_fix=True,
                    ))

        return issues

    def fix(self, soup: BeautifulSoup, html: str) -> Tuple[BeautifulSoup, str, List[FixApplied]]:
        fixes = []
        class_styles = self._get_class_styles(soup)

        if not class_styles:
            return soup, html, fixes

        for cls, props in class_styles.items():
            # Parse the class properties into a dict
            prop_dict = {}
            for decl in props.split(';'):
                decl = decl.strip()
                if ':' in decl:
                    name, val = decl.split(':', 1)
                    name = name.strip().lower()
                    if name in CRITICAL_INLINE_PROPS:
                        prop_dict[name] = val.strip()

            if not prop_dict:
                continue

            elements = soup.find_all(class_=lambda c: c and cls in c.split())
            for el in elements:
                inline = el.get('style', '')
                additions = []

                for prop_name, prop_val in prop_dict.items():
                    if prop_name not in inline:
                        additions.append(f"{prop_name}: {prop_val}")

                if additions:
                    separator = '; ' if inline and not inline.rstrip().endswith(';') else ' '
                    if inline:
                        new_style = inline.rstrip('; ') + '; ' + '; '.join(additions) + ';'
                    else:
                        new_style = '; '.join(additions) + ';'
                    el['style'] = new_style
                    fixes.append(FixApplied(
                        rule=self.name,
                        description=f"Inlined critical styles from .{cls}",
                        before=f"<{el.name}> missing inline: {', '.join(additions[:3])}",
                        after=f"Added: {'; '.join(additions[:3])}",
                    ))

        if fixes:
            html = str(soup)
        return soup, html, fixes
