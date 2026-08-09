import os
import sys
import json
import subprocess
import shutil
from datetime import datetime
from jinja2 import Environment, Template, meta

import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

def _get_writable_output_dir():
    default_dir = os.path.join(BASE_DIR, 'output')
    try:
        os.makedirs(default_dir, exist_ok=True)
        test_file = os.path.join(default_dir, '.write_test')
        with open(test_file, 'w') as f:
            f.write('ok')
        os.remove(test_file)
        return default_dir
    except (OSError, PermissionError):
        tmp_dir = os.path.join(tempfile.gettempdir(), 'pdf_automation_output')
        os.makedirs(tmp_dir, exist_ok=True)
        return tmp_dir

OUTPUT_DIR = _get_writable_output_dir()
os.makedirs(TEMPLATES_DIR, exist_ok=True)

def render_html_template(template_path_or_string, data):
    """
    Renders a Jinja2 HTML template with provided data dictionary.
    """
    if os.path.exists(template_path_or_string):
        with open(template_path_or_string, 'r', encoding='utf-8') as f:
            template_str = f.read()
    else:
        template_str = template_path_or_string
        
    template = Template(template_str)
    return template.render(**data)

def extract_template_variables(template_str_or_path):
    """
    Automatically detects all Jinja2 {{ placeholders }} inside a template string or file.
    """
    if os.path.exists(template_str_or_path):
        with open(template_str_or_path, 'r', encoding='utf-8') as f:
            template_str = f.read()
    else:
        template_str = template_str_or_path
        
    try:
        env = Environment()
        ast = env.parse(template_str)
        undeclared = meta.find_undeclared_variables(ast)
        # Exclude common built-in filters/functions if any
        return sorted(list(undeclared))
    except Exception as e:
        print(f"[WARNING] Could not parse template variables: {e}")
        return []

def list_templates():
    """
    Lists all available HTML templates in the templates directory along with detected variables.
    Supports reading custom templates from /tmp on serverless environments.
    """
    templates_list = []
    dirs_to_check = [TEMPLATES_DIR]
    custom_tmp_dir = os.path.join(tempfile.gettempdir(), 'pdf_automation_templates')
    if os.path.exists(custom_tmp_dir) and custom_tmp_dir != TEMPLATES_DIR:
        dirs_to_check.append(custom_tmp_dir)
        
    seen = set()
    for d in dirs_to_check:
        if os.path.exists(d):
            for fname in os.listdir(d):
                if fname.endswith('.html') and fname not in seen:
                    seen.add(fname)
                    fpath = os.path.join(d, fname)
                    vars_list = extract_template_variables(fpath)
                    templates_list.append({
                        'filename': fname,
                        'name': fname.rsplit('.', 1)[0].replace('_', ' ').title(),
                        'path': fpath,
                        'variables': vars_list,
                        'is_custom': fname not in ['offer_letter.html', 'certificate.html']
                    })
    return templates_list

def save_custom_template(template_name, html_content):
    """
    Saves a new HTML template to the templates directory after validating Jinja2 syntax.
    Falls back to /tmp/pdf_automation_templates on read-only serverless filesystems.
    """
    if not template_name.endswith('.html'):
        safe_name = template_name.lower().replace(' ', '_') + '.html'
    else:
        safe_name = template_name.lower().replace(' ', '_')
        
    # Validate Jinja2 syntax first
    try:
        env = Environment()
        env.parse(html_content)
    except Exception as e:
        raise ValueError(f"Invalid Jinja2 HTML Template Syntax: {e}")
        
    target_path = os.path.join(TEMPLATES_DIR, safe_name)
    try:
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    except (PermissionError, OSError):
        custom_tmp_dir = os.path.join(tempfile.gettempdir(), 'pdf_automation_templates')
        os.makedirs(custom_tmp_dir, exist_ok=True)
        target_path = os.path.join(custom_tmp_dir, safe_name)
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
    detected_vars = extract_template_variables(target_path)
    print(f"[OK] Custom template saved successfully: {target_path} (Detected variables: {detected_vars})")
    return safe_name, target_path, detected_vars

def delete_template(template_name):
    """
    Deletes a template file from system or /tmp templates directory.
    """
    if not template_name.endswith('.html'):
        template_name += '.html'
        
    target_path = os.path.join(TEMPLATES_DIR, template_name)
    custom_tmp_path = os.path.join(tempfile.gettempdir(), 'pdf_automation_templates', template_name)
    
    deleted = False
    if os.path.exists(target_path):
        try:
            os.remove(target_path)
            deleted = True
        except (PermissionError, OSError):
            pass
            
    if os.path.exists(custom_tmp_path):
        try:
            os.remove(custom_tmp_path)
            deleted = True
        except (PermissionError, OSError):
            pass
            
    if deleted:
        print(f"[OK] Template '{template_name}' removed successfully.")
        return True
    else:
        raise FileNotFoundError(f"Template '{template_name}' does not exist.")

def find_browser():
    """
    Finds available Edge or Chrome binary for headless PDF printing.
    """
    possible_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("msedge"),
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser")
    ]
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    return None

def convert_html_to_pdf(html_content, output_filename, temp_html_path=None):
    """
    Converts HTML string to PDF using available PDF engines:
    1. Headless Browser (Edge/Chrome) - Best for modern CSS3, gradients, flexbox & custom fonts
    2. xhtml2pdf - Lightweight pure-python fallback (Serverless compatible)
    3. WeasyPrint - Paged media engine fallback
    """
    pdf_generated = False
    error_messages = []
    
    if not os.path.isabs(output_filename):
        output_filename = os.path.join(OUTPUT_DIR, output_filename)
    else:
        output_filename = os.path.abspath(output_filename)

    if not temp_html_path:
        temp_html_path = output_filename.rsplit('.', 1)[0] + '.html'
    else:
        temp_html_path = os.path.abspath(temp_html_path)

    # Save rendered HTML file first
    try:
        with open(temp_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"[OK] Rendered HTML saved to: {temp_html_path}")
    except (PermissionError, OSError):
        # Fallback to temp directory if output path is read-only
        base_name = os.path.basename(temp_html_path)
        temp_html_path = os.path.join(tempfile.gettempdir(), base_name)
        pdf_name = os.path.basename(output_filename)
        output_filename = os.path.join(tempfile.gettempdir(), pdf_name)
        with open(temp_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    # Method 0: Try Playwright Chromium (Pixel-perfect browser engine)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"])
            page = browser.new_page()
            page.set_content(html_content, wait_until="load")
            page.pdf(path=output_filename, print_background=True, format="A4", landscape=True, margin={"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"})
            browser.close()
            if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
                print(f"[OK] PDF successfully generated using Playwright Chromium: {output_filename}")
                pdf_generated = True
                return output_filename
    except Exception as e:
        error_messages.append(f"Playwright error: {str(e)}")

    # Method 1: Try Headless Edge / Chrome
    browser_exe = find_browser()
    if browser_exe:
        try:
            file_url = f"file:///{temp_html_path.replace('\\', '/')}"
            for headless_flag in ["--headless=new", "--headless"]:
                cmd = [
                    browser_exe,
                    headless_flag,
                    "--no-sandbox",
                    "--disable-gpu",
                    "--no-pdf-header-footer",
                    "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=2000",
                    "--print-to-pdf=" + output_filename,
                    file_url
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
                if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
                    print(f"[OK] PDF successfully generated using Headless Browser ({os.path.basename(browser_exe)}): {output_filename}")
                    pdf_generated = True
                    return output_filename
            error_messages.append(f"Headless browser exit code {result.returncode}: {result.stderr}")
        except Exception as e:
            error_messages.append(f"Headless browser error: {str(e)}")

    # Method 2: Try xhtml2pdf
    if not pdf_generated:
        try:
            from xhtml2pdf import pisa
            clean_html = html_content
            # Strip 100% table heights which cause ReportLab TypeError in xhtml2pdf
            clean_html = clean_html.replace('height="100%"', '').replace("height='100%'", '').replace('height: 100%;', '')

            css_var_map = {
                "var(--ink)": "#12141C",
                "var(--muted)": "#5B6270",
                "var(--faint)": "#9198A6",
                "var(--line)": "#E7E9EE",
                "var(--cyan)": "#1EC8F0",
                "var(--blue)": "#2F6DF6",
                "var(--violet)": "#8B3DF5",
                "var(--magenta)": "#D537D6",
                "var(--paper)": "#FFFFFF"
            }
            for var_key, hex_val in css_var_map.items():
                clean_html = clean_html.replace(var_key, hex_val)

            with open(output_filename, "wb") as pdf_file:
                pisa_status = pisa.CreatePDF(clean_html, dest=pdf_file)
            if not pisa_status.err and os.path.exists(output_filename):
                print(f"[OK] PDF successfully generated using xhtml2pdf: {output_filename}")
                pdf_generated = True
                return output_filename
            else:
                error_messages.append(f"xhtml2pdf error: status_err={pisa_status.err}")
        except Exception as e:
            error_messages.append(f"xhtml2pdf error: {str(e)}")

    # Method 3: Try WeasyPrint
    if not pdf_generated:
        try:
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(output_filename)
            print(f"[OK] PDF successfully generated using WeasyPrint: {output_filename}")
            pdf_generated = True
            return output_filename
        except Exception as e:
            error_messages.append(f"WeasyPrint error: {str(e)}")

    if not pdf_generated:
        raise RuntimeError(f"Could not generate PDF. Errors encountered:\n" + "\n".join(error_messages))

def generate_document(template_name_or_path, data, output_filename):
    """
    Full pipeline: Renders Jinja2 HTML draft with dynamic data and exports to PDF.
    """
    print(f"Generating document for '{data.get('name', 'Recipient')}' -> {output_filename}...")
    
    # 1. Render Jinja2 Template
    rendered_html = render_html_template(template_name_or_path, data)
    
    # 2. Convert to PDF
    pdf_path = convert_html_to_pdf(rendered_html, output_filename)
    return pdf_path

if __name__ == "__main__":
    print("Templates Available:")
    for t in list_templates():
        print(f" - {t['filename']}: Variables={t['variables']}")

