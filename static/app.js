/* TemplateChecker - Client-side interactivity */

document.addEventListener('DOMContentLoaded', function () {

    // --- File validation ---
    var fileInputs = document.querySelectorAll('input[type="file"]');
    var MAX_SIZE = 2 * 1024 * 1024; // 2 MB
    var ALLOWED = ['.html', '.htm'];

    fileInputs.forEach(function (input) {
        input.addEventListener('change', function () {
            var file = this.files[0];
            if (!file) return;

            var ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
            if (ALLOWED.indexOf(ext) === -1) {
                alert('Please select an HTML file (.html or .htm)');
                this.value = '';
                return;
            }

            if (file.size > MAX_SIZE) {
                alert('File is too large. Maximum size is 2 MB.');
                this.value = '';
                return;
            }

            // Update label text with filename
            var label = this.parentElement.querySelector('.upload-text');
            if (label) {
                label.textContent = file.name;
            }
        });
    });

    // --- Drag and drop ---
    var uploadAreas = document.querySelectorAll('.upload-area');
    uploadAreas.forEach(function (area) {
        area.addEventListener('dragover', function (e) {
            e.preventDefault();
            this.classList.add('dragover');
        });

        area.addEventListener('dragleave', function () {
            this.classList.remove('dragover');
        });

        area.addEventListener('drop', function (e) {
            e.preventDefault();
            this.classList.remove('dragover');
            var input = this.querySelector('input[type="file"]');
            if (e.dataTransfer.files.length > 0) {
                input.files = e.dataTransfer.files;
                input.dispatchEvent(new Event('change'));
            }
        });
    });

    // --- Tabs ---
    var tabs = document.querySelectorAll('.tab');
    tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            var tabName = this.getAttribute('data-tab');

            // Deactivate all tabs and content
            this.parentElement.querySelectorAll('.tab').forEach(function (t) {
                t.classList.remove('active');
            });
            document.querySelectorAll('.tab-content').forEach(function (c) {
                c.classList.remove('active');
            });

            // Activate clicked tab and its content
            this.classList.add('active');
            var content = document.getElementById('tab-' + tabName);
            if (content) {
                content.classList.add('active');
            }
        });
    });

    // --- Comparator: require either dropdown or file upload for reference ---
    var comparatorForm = document.getElementById('comparator-form');
    if (comparatorForm) {
        comparatorForm.addEventListener('submit', function (e) {
            var select = document.getElementById('reference');
            var fileInput = document.getElementById('reference-file');

            if (!select.value && (!fileInput.files || fileInput.files.length === 0)) {
                e.preventDefault();
                alert('Please select a reference template from the dropdown or upload a reference file.');
            }
        });
    }

    // --- Scroll to diagnosed results if present ---
    var diagnosedResults = document.getElementById('diagnosed-results');
    if (diagnosedResults) {
        diagnosedResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});
