"""Configuration constants for TemplateChecker."""

import os

# File upload limits
MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2 MB
ALLOWED_EXTENSIONS = {'.html', '.htm'}

# Templates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Templates')

# Gmail style block character limit
GMAIL_STYLE_BLOCK_LIMIT = 8192

# Web-safe font stacks (custom font -> fallback stack)
WEB_SAFE_FALLBACKS = {
    'dm sans': "Arial, Helvetica, sans-serif",
    'lora': "Georgia, 'Times New Roman', Times, serif",
    'open sans': "Arial, Helvetica, sans-serif",
    'roboto': "Arial, Helvetica, sans-serif",
    'montserrat': "Arial, Helvetica, sans-serif",
    'poppins': "Arial, Helvetica, sans-serif",
    'playfair display': "Georgia, 'Times New Roman', Times, serif",
    'merriweather': "Georgia, 'Times New Roman', Times, serif",
    'lato': "Arial, Helvetica, sans-serif",
    'nunito': "Arial, Helvetica, sans-serif",
    'raleway': "Arial, Helvetica, sans-serif",
    'source sans pro': "Arial, Helvetica, sans-serif",
    'inter': "Arial, Helvetica, sans-serif",
}

# Generic web-safe fonts (these don't need fallbacks)
WEB_SAFE_FONTS = {
    'arial', 'helvetica', 'times new roman', 'times', 'courier new',
    'courier', 'georgia', 'verdana', 'tahoma', 'trebuchet ms',
    'palatino', 'garamond', 'bookman', 'comic sans ms', 'impact',
    'lucida console', 'lucida sans unicode', 'segoe ui',
    'sans-serif', 'serif', 'monospace', 'cursive', 'fantasy',
}

# CSS properties unsupported or problematic in major email clients
# Maps property name -> dict of {client: support_level}
UNSUPPORTED_CSS = {
    'flex': {
        'description': 'Flexbox layout',
        'clients': ['Gmail', 'Outlook', 'Yahoo'],
        'severity': 'error',
    },
    'grid': {
        'description': 'CSS Grid layout',
        'clients': ['Gmail', 'Outlook', 'Yahoo'],
        'severity': 'error',
    },
    'display: flex': {
        'description': 'Flexbox layout',
        'clients': ['Gmail', 'Outlook', 'Yahoo'],
        'severity': 'error',
    },
    'display: grid': {
        'description': 'CSS Grid layout',
        'clients': ['Gmail', 'Outlook', 'Yahoo'],
        'severity': 'error',
    },
    'position': {
        'description': 'CSS positioning (relative/absolute/fixed)',
        'clients': ['Gmail', 'Outlook'],
        'severity': 'warning',
        'safe_values': {'static'},
    },
    'box-shadow': {
        'description': 'Box shadow effects',
        'clients': ['Outlook'],
        'severity': 'warning',
    },
    'border-radius': {
        'description': 'Rounded corners',
        'clients': ['Outlook (Windows)'],
        'severity': 'info',
    },
    'opacity': {
        'description': 'Element opacity',
        'clients': ['Outlook'],
        'severity': 'warning',
    },
    'white-space-collapse': {
        'description': 'White space collapsing behavior',
        'clients': ['Gmail', 'Outlook', 'Yahoo'],
        'severity': 'warning',
    },
    'background-image': {
        'description': 'CSS background images',
        'clients': ['Outlook (Windows)'],
        'severity': 'warning',
    },
    'float': {
        'description': 'Float positioning',
        'clients': ['Outlook'],
        'severity': 'warning',
    },
    'max-width': {
        'description': 'Maximum width constraint',
        'clients': ['Outlook (Windows)'],
        'severity': 'info',
    },
}

# Iterable template variable pattern
ITERABLE_VAR_PATTERN = r'\{\{[^}]+\}\}'
