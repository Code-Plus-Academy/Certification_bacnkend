# 📜 PolyCert — Dynamic HTML Templating & PDF Generation Engine

**PolyCert** is an enterprise-grade automated PDF generation and HTML templating engine. Built with Python, Jinja2, and Playwright Headless Chromium, **PolyCert** turns dynamic HTML/CSS templates into pixel-perfect **Certificates**, **Offer Letters**, and custom credentials, with instant cloud storage uploads to **Supabase**, **Cloudinary**, and **AWS S3**.

---

## 🌟 Key Features

1. **Pixel-Perfect Browser Engine (Playwright Chromium & Headless Browser)**
   - Supports modern CSS3 features: **Flexbox, CSS Grid, Glassmorphism, Google Fonts (`Space Grotesk`, `Inter`, `Dancing Script`), gradients, and exact A4/landscape print layouts**.

2. **Automated Multi-Engine Fallback System**
   - **Playwright Chromium**: Primary browser rendering engine for server and local environments.
   - **Headless Chrome / Edge**: System browser printing fallback.
   - **xhtml2pdf & WeasyPrint**: Pure Python paged media fallback engines with automatic table-height & CSS variable sanitization.

3. **Digital Signatures & Custom Credentials**
   - **Handwritten Cursive Scripts**: Automatic rendering of Google Font cursive signatures (`signature_text`).
   - **Image & Data URIs**: Native rendering of PNG/SVG image URLs and Base64 Data URIs (`signature_image`).

4. **Automatic Cloud Storage Ingestion**
   - Built-in multi-provider cloud uploader for **Supabase Storage**, **Cloudinary**, and **AWS S3** with auto-bucket provisioning and public CDN links.

5. **Multi-Channel Integration Workflows**
   - **REST API (`app.py`)**: Protected by API Access Keys (`X-API-Key`) with single (`/api/generate-certificate-info`) and bulk JSON/ZIP endpoints (`/api/generate-batch-info`).
   - **Web Studio Dashboard (`app.py`)**: Modern Flask web dashboard for template editing, Jinja2 variable detection, live HTML preview, and 1-click PDF download.
   - **CLI & Batch CSV Processing (`cli.py`)**: Process candidates from CSV/JSON inputs automatically.

---

## 📁 Project Structure

```
PolyCert/
├── templates/
│   ├── certificate_of_compleation.html  # Modern Certificate template with side panel
│   ├── certificate.html                 # Print-optimized Jinja2 Certificate template
│   └── offer_letter.html                # Employment Offer Letter template
├── generator.py                         # Core Jinja2 render & Playwright/Headless PDF engine
├── cloud_uploader.py                    # Supabase, Cloudinary & AWS S3 auto-uploader
├── app.py                               # Flask Web Studio Dashboard & REST API
├── cli.py                               # CLI tool & CSV batch processor
├── API_DOCUMENTATION.md                 # Complete API integration guide
├── build.sh                             # Render build script with Playwright setup
└── requirements.txt                     # System Python dependencies
```

---

## 🚀 Quick Start

### 1. Run Server Locally
```bash
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser to access the **PolyCert Studio Dashboard**.

### 2. Generate PDF via API
```bash
curl -X POST http://127.0.0.1:5000/api/generate-certificate-info \
  -H "X-API-Key: cpa_sk_89f2a71e4b9d0831" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "certificate_of_compleation.html",
    "data": {
      "name": "Sayaji Kapse",
      "role": "Senior Software Engineer & AI Specialist",
      "serial_no": "POLYCERT-2026-001"
    }
  }'
```
