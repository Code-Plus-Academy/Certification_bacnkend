import os
import json
import csv
from datetime import datetime
from flask import Flask, render_template_string, request, send_file, redirect, url_for, jsonify, flash, session
from generator import (
    generate_document, 
    render_html_template, 
    convert_html_to_pdf, 
    list_templates, 
    save_custom_template, 
    delete_template,
    extract_template_variables,
    TEMPLATES_DIR, 
    OUTPUT_DIR
)

from flask import Request

# Increase Werkzeug/Flask form field memory size limit (default is 500 KB) to 500 MB to support large base64 inline images in HTML templates
Request.max_form_memory_size = 500 * 1024 * 1024  # 500 Megabytes
Request.max_content_length = 500 * 1024 * 1024     # 500 Megabytes

app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = "pdf_automation_secret_key"
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB max payload limit

# Async background pre-installation of Playwright Chromium on server boot
import threading
import subprocess
import sys

def _async_install_playwright():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
                browser.close()
            except Exception:
                print("[STARTUP] Pre-installing Playwright Chromium binaries on server startup...")
                subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
    except Exception as e:
        print(f"[STARTUP] Playwright check note: {e}")

threading.Thread(target=_async_install_playwright, daemon=True).start()

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PolyCert Studio — Admin Login</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0A0D14;
            --card-bg: #121824;
            --border: #232D3F;
            --accent-blue: #2F6DF6;
            --accent-cyan: #1EC8F0;
            --accent-violet: #8B3DF5;
            --text-main: #F1F5F9;
            --text-muted: #94A3B8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }
        .login-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 40px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            text-align: center;
        }
        .logo {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-violet));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .subtitle {
            font-size: 14px;
            color: var(--text-muted);
            margin-bottom: 30px;
        }
        .form-group {
            text-align: left;
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-muted);
            margin-bottom: 8px;
        }
        input {
            width: 100%;
            padding: 14px;
            background: #0B0E17;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
            font-family: monospace;
            transition: border-color 0.2s;
        }
        input:focus {
            border-color: var(--accent-blue);
            outline: none;
        }
        .btn-submit {
            width: 100%;
            padding: 14px;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-violet));
            color: #fff;
            border: none;
            border-radius: 8px;
            font-weight: 700;
            font-size: 15px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(47, 109, 246, 0.4);
            transition: transform 0.1s, opacity 0.2s;
        }
        .btn-submit:hover { opacity: 0.95; }
        .btn-submit:active { transform: scale(0.98); }
        .alert-error {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.4);
            color: #F87171;
            padding: 12px;
            border-radius: 8px;
            font-size: 13px;
            margin-bottom: 20px;
        }
        .key-hint {
            margin-top: 24px;
            font-size: 11px;
            color: var(--text-muted);
            background: #0B0E17;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid var(--border);
        }
    </style>
</head>
<body>

<div class="login-card">
    <div class="logo">📜 PolyCert Studio</div>
    <div class="subtitle">Admin Authentication Required</div>

    {% if error %}
    <div class="alert-error">⚠️ {{ error }}</div>
    {% endif %}

    <form method="POST" action="/login">
        <input type="hidden" name="next" value="{{ next_url }}">
        <div class="form-group">
            <label>Server Access Key / Admin Password</label>
            <input type="password" name="api_key" placeholder="Enter server access key..." required autofocus>
        </div>

        <button type="submit" class="btn-submit">🔓 Unlock Dashboard</button>
    </form>

    <div class="key-hint">
        🔒 Protected by <code>API_ACCESS_KEY</code>
    </div>
</div>

</body>
</html>
"""

@app.before_request
def handle_authentication():
    expected_key = os.environ.get("API_ACCESS_KEY") or os.environ.get("SERVER_API_KEY")

    # 1. Allow login page, static assets, and public output downloads freely
    public_paths = ['/login', '/logout', '/static/', '/output/']
    if any(request.path.startswith(p) for p in public_paths) or request.endpoint == 'static':
        return None

    # 2. Determine if incoming request is an API request or Browser request
    is_api_request = (
        request.path.startswith('/api/') or
        'X-API-Key' in request.headers or
        'x-api-key' in request.headers or
        'Authorization' in request.headers or
        request.headers.get('Accept') == 'application/json' or
        request.is_json
    )

    if is_api_request:
        if not expected_key:
            return None  # No API key configured -> allow

        # 🔑 API Authentication Logic
        auth_header = request.headers.get('Authorization', '')
        bearer_token = auth_header.replace('Bearer ', '').strip() if auth_header.startswith('Bearer ') else ''

        provided_key = (
            request.headers.get('X-API-Key') or 
            request.headers.get('x-api-key') or 
            bearer_token or 
            request.args.get('api_key')
        )

        if provided_key == expected_key:
            return None  # ✅ Valid Key -> Process API request

        # ❌ Invalid / Missing API Key -> Return 401 JSON (No 302 Redirect!)
        return jsonify({
            "status": "error",
            "error": "Unauthorized: Invalid or missing API access key",
            "message": "Please provide your server access key via 'X-API-Key' header or 'Authorization: Bearer <key>'"
        }), 401

    # 3. 🌐 Browser / Web Dashboard Logic
    if expected_key and not session.get('authenticated'):
        # Redirect browser users to login page
        return redirect(url_for('login', next=request.url))

@app.route('/login', methods=['GET', 'POST'])
def login():
    expected_key = os.environ.get("API_ACCESS_KEY") or os.environ.get("SERVER_API_KEY")
    if not expected_key:
        session['authenticated'] = True
        return redirect(url_for('index'))

    next_url = request.args.get('next') or request.form.get('next') or url_for('index')
    error = None

    if request.method == 'POST':
        provided_key = request.form.get('api_key', '').strip()
        if provided_key == expected_key:
            session['authenticated'] = True
            return redirect(next_url)
        else:
            error = "Invalid API Access Key or Admin Password"

    return render_template_string(LOGIN_HTML, error=error, next_url=next_url)

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.errorhandler(413)
def request_entity_too_large(error):
    flash("Request Entity Too Large: The transmitted HTML template or data exceeds the capacity limit (Max allowed is 500 MB). Please reduce embedded image sizes or upload external assets.")
    return redirect('/?tab=templates')

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PolyCert Studio — Enterprise HTML Templating & PDF Generator</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0A0D14;
            --card-bg: #121824;
            --border: #232D3F;
            --accent-blue: #2F6DF6;
            --accent-cyan: #1EC8F0;
            --accent-violet: #8B3DF5;
            --accent-danger: #EF4444;
            --text-main: #F1F5F9;
            --text-muted: #94A3B8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            padding: 30px 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1240px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 35px;
        }

        header h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 36px;
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-violet));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 8px;
        }

        header p {
            color: var(--text-muted);
            font-size: 15px;
        }

        .nav-tabs {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 12px;
        }

        .nav-tab {
            padding: 10px 20px;
            border-radius: 12px;
            background: #121824;
            color: var(--text-muted);
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            border: 1px solid var(--border);
            text-decoration: none;
            transition: all 0.2s;
        }

        .nav-tab.active {
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-violet));
            color: #fff;
            border-color: var(--accent-blue);
            box-shadow: 0 4px 14px rgba(47, 109, 246, 0.3);
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }

        @media (max-width: 900px) {
            .grid { grid-template-columns: 1fr; }
        }

        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 28px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        .card h2 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 20px;
            margin-bottom: 20px;
            color: var(--accent-cyan);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .form-group {
            margin-bottom: 18px;
        }

        label {
            display: block;
            font-size: 12px;
            font-weight: 700;
            color: var(--text-muted);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        input[type="text"], select, textarea {
            width: 100%;
            padding: 12px 14px;
            background: #0B0E17;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.2s;
        }

        textarea {
            font-family: monospace;
            font-size: 13px;
            resize: vertical;
        }

        input:focus, select:focus, textarea:focus {
            border-color: var(--accent-blue);
            outline: none;
        }

        .btn-group {
            display: flex;
            gap: 12px;
            margin-top: 24px;
        }

        .btn {
            flex: 1;
            padding: 14px;
            border: none;
            border-radius: 8px;
            font-weight: 700;
            font-size: 14px;
            cursor: pointer;
            transition: transform 0.1s, opacity 0.2s;
            text-align: center;
            text-decoration: none;
            display: inline-block;
        }

        .btn:active { transform: scale(0.98); }

        .btn-primary {
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-violet));
            color: #fff;
            box-shadow: 0 4px 15px rgba(47, 109, 246, 0.4);
        }

        .btn-secondary {
            background: #232D3F;
            color: var(--text-main);
        }

        .btn-danger {
            background: rgba(239, 68, 68, 0.15);
            color: var(--accent-danger);
            border: 1px solid rgba(239, 68, 68, 0.3);
            padding: 6px 12px;
            font-size: 12px;
            border-radius: 6px;
        }

        .btn-primary:hover, .btn-secondary:hover, .btn-danger:hover { opacity: 0.9; }

        .alert-info {
            padding: 14px;
            background: rgba(30, 200, 240, 0.1);
            border: 1px solid var(--accent-cyan);
            border-radius: 8px;
            color: var(--accent-cyan);
            font-size: 14px;
            margin-bottom: 20px;
        }

        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
            background: #232D3F;
            color: var(--accent-cyan);
        }

        .var-chip {
            display: inline-block;
            background: #0B0E17;
            border: 1px solid var(--border);
            color: #38BDF8;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-family: monospace;
            margin: 3px;
        }

        .template-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px;
            background: #0B0E17;
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 10px;
        }

        .template-item .t-info h4 {
            font-size: 14px;
            color: #fff;
        }

        .template-item .t-info p {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
        }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>📜 PolyCert Studio</h1>
        <p>Generate, Add & Manage Custom HTML Templates for Offer Letters & Certificates</p>
    </header>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="alert-info">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <div class="nav-tabs">
        <a href="/?tab=generate" class="nav-tab {% if active_tab == 'generate' %}active{% endif %}">📄 Generate PDF</a>
        <a href="/?tab=templates" class="nav-tab {% if active_tab == 'templates' %}active{% endif %}">➕ Manage Custom HTML Templates</a>
        <a href="/guide" target="_blank" class="nav-tab">📖 HTML Draft Structure Guide</a>
        <a href="/logout" class="nav-tab" style="margin-left: auto; background: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.3);">🔒 Logout</a>
    </div>

    {% if active_tab == 'generate' %}
    <div class="grid">
        <!-- FORM CARD -->
        <div class="card">
            <h2>
                <span>📄 Dynamic PDF Generation</span>
            </h2>

            <form action="/select-template" method="GET" style="margin-bottom: 24px;">
                <input type="hidden" name="tab" value="generate">
                <div class="form-group">
                    <label>Select Template</label>
                    <select name="template" onchange="this.form.submit()">
                        {% for t in all_templates %}
                        <option value="{{ t.filename }}" {% if selected_template.filename == t.filename %}selected{% endif %}>
                            {{ t.name }} ({{ t.filename }}) {% if t.is_custom %}[Custom]{% endif %}
                        </option>
                        {% endfor %}
                    </select>
                </div>
            </form>

            <form action="/generate" method="POST" target="_blank">
                <input type="hidden" name="template_filename" value="{{ selected_template.filename }}">

                <div style="margin-bottom: 18px;">
                    <label style="color: var(--accent-cyan);">Detected Jinja2 Placeholders:</label>
                    <div>
                        {% for v in selected_template.variables %}
                        <span class="var-chip">&#123;&#123; {{ v }} &#125;&#125;</span>
                        {% else %}
                        <span style="color: var(--text-muted); font-size: 13px;">No Jinja2 placeholders detected in this template.</span>
                        {% endfor %}
                    </div>
                </div>

                {% for var in selected_template.variables %}
                <div class="form-group">
                    <label>{{ var|replace('_', ' ')|upper }}</label>
                    <input type="text" name="{{ var }}" value="{{ default_values.get(var, '') }}" required>
                </div>
                {% endfor %}

                <div class="btn-group">
                    <button type="submit" name="action" value="pdf" class="btn btn-primary">📥 Download PDF</button>
                    <button type="submit" name="action" value="preview" class="btn btn-secondary">👁️ Live Preview HTML</button>
                </div>
            </form>
        </div>

        <!-- RECENT FILES & INFO CARD -->
        <div class="card">
            <h2>⚙️ Template Summary</h2>
            <div style="background: #0B0E17; padding: 18px; border-radius: 8px; border: 1px solid var(--border); font-size: 13px; line-height: 1.6; margin-bottom: 20px;">
                <p><strong>Selected Template:</strong> <span style="color: var(--accent-cyan);">{{ selected_template.filename }}</span></p>
                <p><strong>Template Path:</strong> {{ selected_template.path }}</p>
                <p><strong>Required Fields:</strong> {{ selected_template.variables|length }} fields</p>
            </div>

            <h2>📁 Recent Output PDFs</h2>
            <ul style="list-style: none; color: var(--text-muted); font-size: 13px;">
                {% for f in recent_files %}
                <li style="margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    • <a href="/output/{{ f }}" target="_blank" style="color: var(--accent-cyan); text-decoration: none; font-weight: 600;">{{ f }}</a>
                </li>
                {% else %}
                <li style="color: var(--text-muted);">No output files generated yet.</li>
                {% endfor %}
            </ul>
        </div>
    </div>

    {% elif active_tab == 'templates' %}
    <div class="grid">
        <!-- ADD TEMPLATE CARD -->
        <div class="card">
            <h2>➕ Add Custom HTML Template</h2>
            <form action="/add-template" method="POST">
                <div class="form-group">
                    <label>Template Name (Identifier)</label>
                    <input type="text" name="template_name" placeholder="e.g. Internship_Offer_Letter" required>
                </div>

                <div class="form-group">
                    <label>Paste HTML Draft Content (Jinja2 Formatted)</label>
                    <textarea name="html_content" rows="16" placeholder="<!DOCTYPE html>&#10;<html>&#10;<head>&#10;  <style>@page { size: A4; margin: 20mm; }</style>&#10;</head>&#10;<body>&#10;  <h1>Offer Letter for {{ name }}</h1>&#10;  <p>Position: {{ role }}</p>&#10;</body>&#10;</html>" required></textarea>
                </div>

                <button type="submit" class="btn btn-primary" style="width: 100%;">💾 Save Custom Template</button>
            </form>
        </div>

        <!-- LIST & REMOVE TEMPLATES CARD -->
        <div class="card">
            <h2>📋 Installed Templates</h2>
            <div>
                {% for t in all_templates %}
                <div class="template-item">
                    <div class="t-info">
                        <h4>{{ t.name }} <span class="badge">{{ t.filename }}</span></h4>
                        <p>Placeholders: {{ t.variables|join(', ') if t.variables else 'None' }}</p>
                    </div>
                    {% if t.is_custom %}
                    <form action="/delete-template" method="POST" onsubmit="return confirm('Are you sure you want to delete template {{ t.filename }}?');">
                        <input type="hidden" name="template_filename" value="{{ t.filename }}">
                        <button type="submit" class="btn btn-danger">🗑️ Delete</button>
                    </form>
                    {% else %}
                    <span style="font-size: 11px; color: var(--text-muted); font-weight: 600;">System Default</span>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    {% endif %}
</div>

</body>
</html>
"""

DEFAULT_FIELD_VALUES = {
    "name": "Sayaji Kapse",
    "recipient_name": "Sayaji Kapse",
    "role": "Senior Full-Stack & AI Engineer",
    "position": "Senior Full-Stack Developer",
    "duration": "24 Months",
    "serial_no": "KT-2026-08-001",
    "certificate_id": "CPA-2026-SK-8891",
    "company_name": "Kalki Technology Pvt. Ltd.",
    "holding_company": "Neeta Holdings Pvt. Ltd.",
    "organization_name": "Code Plus Academy",
    "signatory": "Dr. Alex Vance",
    "signatory_role": "Director of Engineering",
    "date": datetime.today().strftime('%B %d, %Y'),
    "doc_tag": "VERIFIED CERTIFICATE",
    "eyebrow": "CERTIFICATE OF COMPLETION"
}

@app.route('/')
@app.route('/select-template')
def index():
    tab = request.args.get('tab', 'generate')
    selected_name = request.args.get('template', 'offer_letter.html')
    all_t = list_templates()
    
    selected_t = next((t for t in all_t if t['filename'] == selected_name), all_t[0] if all_t else None)
    recent = os.listdir(OUTPUT_DIR) if os.path.exists(OUTPUT_DIR) else []
    recent_pdfs = [f for f in recent if f.endswith('.pdf')]
    
    return render_template_string(
        INDEX_HTML, 
        active_tab=tab, 
        all_templates=all_t, 
        selected_template=selected_t,
        default_values=DEFAULT_FIELD_VALUES,
        recent_files=recent_pdfs[:8]
    )

import tempfile

def resolve_template_path(template_filename):
    if not template_filename.endswith('.html'):
        template_filename += '.html'
    target_path = os.path.join(TEMPLATES_DIR, template_filename)
    if os.path.exists(target_path):
        return target_path
    fallback_path = os.path.join(tempfile.gettempdir(), 'pdf_automation_templates', template_filename)
    if os.path.exists(fallback_path):
        return fallback_path
    return None

@app.route('/generate', methods=['POST'])
def generate():
    data = request.form.to_dict()
    template_filename = data.get('template_filename', 'offer_letter.html')
    action = data.get('action', 'pdf')
    
    template_file = resolve_template_path(template_filename)
    if not template_file:
        flash(f"Template '{template_filename}' not found.")
        return redirect('/')

    rendered_html = render_html_template(template_file, data)

    if action == 'preview':
        return rendered_html
    else:
        safe_name = data.get('name', 'document').replace(' ', '_')
        pdf_name = f"{template_filename.rsplit('.', 1)[0]}_{safe_name}.pdf"
        pdf_path = os.path.join(OUTPUT_DIR, pdf_name)
        convert_html_to_pdf(rendered_html, pdf_path)
        return send_file(pdf_path, as_attachment=True)

@app.route('/add-template', methods=['POST'])
def add_template():
    t_name = request.form.get('template_name', '').strip()
    html_content = request.form.get('html_content', '').strip()
    
    if not t_name or not html_content:
        flash("Template name and HTML content are required.")
        return redirect('/?tab=templates')
        
    try:
        saved_filename, _, vars_found = save_custom_template(t_name, html_content)
        flash(f"Custom template '{saved_filename}' added successfully! Placeholders detected: {', '.join(vars_found)}")
        return redirect(f'/?tab=generate&template={saved_filename}')
    except Exception as e:
        flash(f"Failed to save template: {str(e)}")
        return redirect('/?tab=templates')

@app.route('/delete-template', methods=['POST'])
def remove_template():
    filename = request.form.get('template_filename', '').strip()
    try:
        delete_template(filename)
        flash(f"Template '{filename}' removed successfully.")
    except Exception as e:
        flash(f"Could not delete template: {str(e)}")
    return redirect('/?tab=templates')

@app.route('/guide')
def guide():
    guide_path = os.path.join(BASE_DIR, 'TEMPLATE_GUIDE.md')
    if os.path.exists(guide_path):
        with open(guide_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"<pre style='background:#121824; color:#fff; padding:30px; font-family:sans-serif; line-height:1.6;'>{content}</pre>"
    return "Guide file not found."

import zipfile
import io

@app.route('/api/templates', methods=['GET'])
def api_list_templates():
    """
    Returns JSON list of all installed templates and their detected Jinja2 placeholders.
    """
    templates = list_templates()
    return jsonify({"status": "success", "templates": templates})

@app.route('/api/templates/<filename>', methods=['GET'])
def api_get_template(filename):
    """
    Returns HTML raw content and detected variables for a specific template.
    """
    target_path = resolve_template_path(filename)
    if not target_path:
        return jsonify({"error": f"Template '{filename}' not found"}), 404
        
    with open(target_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    vars_list = extract_template_variables(target_path)
    return jsonify({
        "status": "success",
        "filename": os.path.basename(target_path),
        "variables": vars_list,
        "html_content": html_content
    })

@app.route('/api/templates', methods=['POST', 'PUT'])
def api_save_template():
    """
    Add or update a custom HTML template.
    JSON Payload: { "name": "Internship_Letter", "html": "<html>...</html>" }
    """
    try:
        req_data = request.get_json(force=True)
        t_name = req_data.get('name', '').strip()
        html_content = req_data.get('html', '').strip()
        
        if not t_name or not html_content:
            return jsonify({"error": "Fields 'name' and 'html' are required"}), 400
            
        saved_filename, _, vars_found = save_custom_template(t_name, html_content)
        return jsonify({
            "status": "success",
            "message": f"Template '{saved_filename}' saved successfully",
            "filename": saved_filename,
            "variables": vars_found
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/templates/<filename>', methods=['DELETE'])
def api_delete_template(filename):
    """
    Deletes a custom HTML template.
    """
    try:
        delete_template(filename)
        return jsonify({"status": "success", "message": f"Template '{filename}' deleted successfully"})
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-batch-pdf', methods=['POST'])
def api_generate_batch_pdf():
    """
    Bulk generation API Endpoint for Express.js.
    Expects JSON body:
    {
      "template": "certificate.html",
      "data_list": [
         { "name": "Alice Smith", "role": "Full Stack Engineer" },
         { "name": "Bob Jones", "role": "AI Architect" }
      ]
    }
    Returns a ZIP file containing all generated PDFs.
    """
    try:
        req_data = request.get_json(force=True)
        template_filename = req_data.get('template', 'certificate.html')
        data_list = req_data.get('data_list', [])
        
        if not data_list or not isinstance(data_list, list):
            return jsonify({"error": "'data_list' array is required for batch generation"}), 400
            
        template_file = resolve_template_path(template_filename)
        if not template_file:
            return jsonify({"error": f"Template '{template_filename}' not found"}), 404

        # Memory buffer for ZIP output
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for idx, item_data in enumerate(data_list, 1):
                if 'date' not in item_data or not item_data['date']:
                    item_data['date'] = datetime.today().strftime('%B %d, %Y')
                
                safe_name = str(item_data.get('name', f'entry_{idx}')).replace(' ', '_')
                pdf_filename = f"{template_filename.rsplit('.', 1)[0]}_{safe_name}.pdf"
                pdf_path = os.path.join(OUTPUT_DIR, f"batch_{pdf_filename}")
                
                rendered = render_html_template(template_file, item_data)
                convert_html_to_pdf(rendered, pdf_path)
                
                # Write PDF into ZIP archive
                zf.write(pdf_path, arcname=pdf_filename)
                
        memory_file.seek(0)
        zip_filename = f"Batch_{template_filename.rsplit('.', 1)[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=zip_filename)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

import uuid
from cloud_uploader import process_cloud_uploads

@app.route('/api/generate-certificate-info', methods=['POST'])
def api_generate_certificate_info():
    """
    Structured Generation API Endpoint.
    Returns complete metadata JSON response including:
    - request_id
    - certificate_serial / serial_no
    - recipient_name
    - template_used
    - file_info (filename, size, local download URL)
    - cloud_storage_urls (Supabase, S3, Cloudinary)
    """
    try:
        req_data = request.get_json(force=True)
        template_filename = req_data.get('template', 'certificate.html')
        data = req_data.get('data', {})
        
        template_file = resolve_template_path(template_filename)
        if not template_file:
            return jsonify({"error": f"Template '{template_filename}' not found"}), 404
            
        request_id = f"req_{str(uuid.uuid4())[:13]}"
        serial_no = data.get('serial_no') or data.get('certificate_id') or f"CERT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        data['serial_no'] = serial_no
        
        rendered_html = render_html_template(template_file, data)
        safe_name = str(data.get('name', 'document')).replace(' ', '_')
        pdf_name = f"cert_{serial_no}_{safe_name}.pdf"
        pdf_path = os.path.join(OUTPUT_DIR, pdf_name)
        
        convert_html_to_pdf(rendered_html, pdf_path)
        
        file_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
        req_base_url = request.host_url
        cloud_urls = process_cloud_uploads(pdf_path, req_base_url)
        
        return jsonify({
            "status": "success",
            "request_id": request_id,
            "certificate_serial": serial_no,
            "recipient_name": data.get('name', 'Recipient'),
            "role_title": data.get('role', ''),
            "template_used": template_filename,
            "generated_at": datetime.now().isoformat(),
            "file_info": {
                "filename": pdf_name,
                "size_bytes": file_size,
                "local_download_url": f"{req_base_url.rstrip('/')}/output/{pdf_name}"
            },
            "cloud_storage_urls": cloud_urls
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-batch-info', methods=['POST'])
def api_generate_batch_info():
    """
    Structured Batch Generation Endpoint.
    Returns JSON list of all generated certificates with request_id, serial, local & cloud storage URLs.
    """
    try:
        req_data = request.get_json(force=True)
        template_filename = req_data.get('template', 'certificate.html')
        data_list = req_data.get('data_list', [])
        
        if not data_list or not isinstance(data_list, list):
            return jsonify({"error": "'data_list' array is required"}), 400
            
        template_file = resolve_template_path(template_filename)
        if not template_file:
            return jsonify({"error": f"Template '{template_filename}' not found"}), 404


        batch_id = f"batch_{str(uuid.uuid4())[:13]}"
        results = []
        req_base_url = request.host_url

        for idx, item_data in enumerate(data_list, 1):
            if 'date' not in item_data or not item_data['date']:
                item_data['date'] = datetime.today().strftime('%B %d, %Y')
            
            req_id = f"req_{str(uuid.uuid4())[:13]}"
            serial = item_data.get('serial_no') or item_data.get('certificate_id') or f"CERT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
            item_data['serial_no'] = serial
            
            safe_name = str(item_data.get('name', f'entry_{idx}')).replace(' ', '_')
            pdf_filename = f"batch_{serial}_{safe_name}.pdf"
            pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
            
            rendered = render_html_template(template_file, item_data)
            convert_html_to_pdf(rendered, pdf_path)
            
            file_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
            cloud_urls = process_cloud_uploads(pdf_path, req_base_url)
            
            results.append({
                "request_id": req_id,
                "certificate_serial": serial,
                "recipient_name": item_data.get('name', ''),
                "role_title": item_data.get('role', ''),
                "file_info": {
                    "filename": pdf_filename,
                    "size_bytes": file_size,
                    "local_download_url": f"{req_base_url.rstrip('/')}/output/{pdf_filename}"
                },
                "cloud_storage_urls": cloud_urls
            })
            
        return jsonify({
            "status": "success",
            "batch_id": batch_id,
            "total_generated": len(results),
            "generated_at": datetime.now().isoformat(),
            "certificates": results
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/output/<filename>')
def serve_output(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    return "File not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    print(f"Starting PDF Automation Studio Web App on http://{host}:{port} ...")
    app.run(host=host, port=port, debug=False)

