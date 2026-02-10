"""Compatibility checker engine: orchestrates all rules."""

from bs4 import BeautifulSoup
from checker.models import CheckReport
from checker.rules.fonts import FontRule
from checker.rules.css_support import CSSSupportRule
from checker.rules.style_block import StyleBlockRule
from checker.rules.inline_css import InlineCSSRule
from checker.rules.images import ImageRule
from checker.rules.layout import LayoutRule
from checker.rules.outlook import OutlookRule
from checker.rules.media_queries import MediaQueryRule
from checker.rules.dark_mode import DarkModeRule

# Rule execution order matters: check all first, then fix in dependency order
ALL_RULES = [
    FontRule(),
    CSSSupportRule(),
    StyleBlockRule(),
    InlineCSSRule(),
    ImageRule(),
    LayoutRule(),
    OutlookRule(),
    MediaQueryRule(),
    DarkModeRule(),
]


def run_checks(html: str) -> CheckReport:
    """Run all compatibility checks on the given HTML.

    Returns a CheckReport with issues found and auto-fixes applied.
    """
    report = CheckReport(original_html=html)

    # Parse once for checking
    soup = BeautifulSoup(html, 'html.parser')

    # Phase 1: Run all checks to find issues
    for rule in ALL_RULES:
        issues = rule.check(soup, html)
        report.issues.extend(issues)

    # Phase 2: Apply fixes (re-parse to get clean state)
    fix_soup = BeautifulSoup(html, 'html.parser')
    fixed_html = html

    # Fix order: media queries first (structural), then style blocks,
    # then inline CSS, then individual properties
    fix_order = [
        MediaQueryRule(),
        StyleBlockRule(),
        CSSSupportRule(),
        InlineCSSRule(),
        FontRule(),
        ImageRule(),
        OutlookRule(),
    ]

    for rule in fix_order:
        fix_soup, fixed_html, fixes = rule.fix(fix_soup, fixed_html)
        report.fixes.extend(fixes)

    report.fixed_html = str(fix_soup)
    return report
