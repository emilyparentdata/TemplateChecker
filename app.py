"""TemplateChecker - Flask web application for email template QA."""

import os
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, send_file, Response
)
from io import BytesIO
from config import TEMPLATES_DIR, MAX_UPLOAD_SIZE, ALLOWED_EXTENSIONS
from checker.engine import run_checks
from comparator.engine import run_comparison, total_differences, diagnose_issue

app = Flask(__name__, template_folder='ui')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-templatechecker-key')
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE


def _allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def _list_templates() -> list:
    """List HTML files in the Templates directory."""
    if not os.path.isdir(TEMPLATES_DIR):
        return []
    return sorted(
        f for f in os.listdir(TEMPLATES_DIR)
        if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route('/')
def index():
    return redirect(url_for('checker'))


@app.route('/checker', methods=['GET', 'POST'])
def checker():
    report = None
    filename = ''

    if request.method == 'POST':
        file = request.files.get('html_file')
        if not file or not file.filename:
            flash('Please select an HTML file.', 'error')
            return render_template('checker.html', active='checker')

        if not _allowed_file(file.filename):
            flash('Only .html and .htm files are allowed.', 'error')
            return render_template('checker.html', active='checker')

        filename = file.filename
        html_content = file.read().decode('utf-8', errors='replace')
        report = run_checks(html_content)

    return render_template('checker.html', active='checker',
                           report=report, filename=filename)


@app.route('/checker/download', methods=['POST'])
def checker_download():
    fixed_html = request.form.get('fixed_html', '')
    filename = request.form.get('filename', 'fixed_email.html')

    if not fixed_html:
        flash('No fixed HTML available.', 'error')
        return redirect(url_for('checker'))

    # Add "fixed_" prefix to filename
    base, ext = os.path.splitext(filename)
    download_name = f"{base}_fixed{ext}"

    buffer = BytesIO(fixed_html.encode('utf-8'))
    return send_file(
        buffer,
        mimetype='text/html',
        as_attachment=True,
        download_name=download_name,
    )


@app.route('/comparator', methods=['GET', 'POST'])
def comparator():
    templates = _list_templates()
    results = None
    total = 0
    selected_ref = ''
    diagnosed = None
    symptom = ''
    reference_html = None
    built_html = None

    if request.method == 'POST':
        # Check if this is a diagnosis submission (HTML passed via hidden fields)
        symptom = request.form.get('symptom', '').strip()
        hidden_ref = request.form.get('reference_html', '')
        hidden_built = request.form.get('built_html', '')

        if hidden_ref and hidden_built:
            # Re-run comparison from stored HTML
            reference_html = hidden_ref
            built_html = hidden_built
            selected_ref = request.form.get('reference', '')
            results = run_comparison(reference_html, built_html)
            total = total_differences(results)

            if symptom:
                diagnosed = diagnose_issue(results, symptom)
        else:
            # Original comparison flow: get reference HTML
            selected_ref = request.form.get('reference', '')

            ref_file = request.files.get('reference_file')
            if ref_file and ref_file.filename:
                if not _allowed_file(ref_file.filename):
                    flash('Reference file must be .html or .htm.', 'error')
                    return render_template('comparator.html', active='comparator',
                                           templates=templates, selected_ref=selected_ref)
                reference_html = ref_file.read().decode('utf-8', errors='replace')
            elif selected_ref:
                ref_path = os.path.join(TEMPLATES_DIR, selected_ref)
                if os.path.isfile(ref_path):
                    with open(ref_path, 'r', encoding='utf-8') as f:
                        reference_html = f.read()
                else:
                    flash('Selected template not found.', 'error')
                    return render_template('comparator.html', active='comparator',
                                           templates=templates, selected_ref=selected_ref)
            else:
                flash('Please select or upload a reference template.', 'error')
                return render_template('comparator.html', active='comparator',
                                       templates=templates, selected_ref=selected_ref)

            # Get built email HTML
            built_file = request.files.get('built_file')
            if not built_file or not built_file.filename:
                flash('Please upload a built email file.', 'error')
                return render_template('comparator.html', active='comparator',
                                       templates=templates, selected_ref=selected_ref)

            if not _allowed_file(built_file.filename):
                flash('Built file must be .html or .htm.', 'error')
                return render_template('comparator.html', active='comparator',
                                       templates=templates, selected_ref=selected_ref)

            built_html = built_file.read().decode('utf-8', errors='replace')
            results = run_comparison(reference_html, built_html)
            total = total_differences(results)

    return render_template('comparator.html', active='comparator',
                           templates=templates, results=results,
                           total=total, selected_ref=selected_ref,
                           diagnosed=diagnosed, symptom=symptom,
                           reference_html=reference_html,
                           built_html=built_html)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
