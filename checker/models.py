"""Data classes for compatibility checker results."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Issue:
    """A single compatibility issue found in the HTML."""
    rule: str           # Rule name (e.g., "fonts", "css_support")
    severity: str       # "error", "warning", or "info"
    message: str        # Human-readable description
    element: str = ""   # The element/selector involved
    line: int = 0       # Approximate line number
    can_fix: bool = False


@dataclass
class FixApplied:
    """A single auto-fix that was applied."""
    rule: str
    description: str
    before: str = ""
    after: str = ""


@dataclass
class CheckReport:
    """Complete report from running all compatibility checks."""
    issues: List[Issue] = field(default_factory=list)
    fixes: List[FixApplied] = field(default_factory=list)
    fixed_html: str = ""
    original_html: str = ""

    @property
    def error_count(self):
        return sum(1 for i in self.issues if i.severity == 'error')

    @property
    def warning_count(self):
        return sum(1 for i in self.issues if i.severity == 'warning')

    @property
    def info_count(self):
        return sum(1 for i in self.issues if i.severity == 'info')

    def issues_by_rule(self) -> dict:
        grouped = {}
        for issue in self.issues:
            grouped.setdefault(issue.rule, []).append(issue)
        return grouped
