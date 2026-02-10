"""Abstract base class for all compatibility rules."""

from abc import ABC, abstractmethod
from typing import List, Tuple
from bs4 import BeautifulSoup
from checker.models import Issue, FixApplied


class BaseRule(ABC):
    """Base class that all checker rules must implement."""

    name: str = "base"
    description: str = ""

    @abstractmethod
    def check(self, soup: BeautifulSoup, html: str) -> List[Issue]:
        """Analyze the HTML and return a list of issues found."""
        ...

    @abstractmethod
    def fix(self, soup: BeautifulSoup, html: str) -> Tuple[BeautifulSoup, str, List[FixApplied]]:
        """Apply auto-fixes and return (modified_soup, modified_html, list_of_fixes).

        If no fixes are possible, return the inputs unchanged with an empty list.
        """
        ...
