# Automated PDF Generation & Templating System

An automated Python solution to dynamically generate **Offer Letters**, **Certificates of Completion**, and custom HTML documents into high-quality PDFs using **Jinja2** and multiple PDF rendering backends (Headless Chrome/Edge, WeasyPrint, xhtml2pdf).

---

## 🌟 Key Features

1. **Jinja2 HTML Template Rendering**
   - Easily inject dynamic fields (`name`, `role`, `duration`, `serial_no`, `date`, `company_name`, `holding_company`, `signatory`, etc.) into HTML drafts.

2. **High-Fidelity PDF Conversion**
   - **Headless Browser Engine (Edge/Chrome)**: Supports modern CSS3 features (Flexbox, CSS Grid, custom Google Fonts like `Space Grotesk` & `Inter`, CSS linear/radial gradients, and exact A4/landscape print layouts).
   - **WeasyPrint & xhtml2pdf Fallbacks**: Pure Python paged media fallback engines.

3. **Multi-Channel Workflows**
   - **Python API (`generator.py`)**: Direct programmatic access for backend integration.
   - **CLI & Batch CSV Processing (`cli.py`)**: Process dozens or hundreds of candidates/students from CSV or JSON inputs automatically.
   - **Web Application (`app.py`)**: Modern Flask web dashboard with live HTML preview & 1-click PDF download.
   - **Netlify Serverless Deployment**: Serverless Python function setup (`netlify.toml`, `serverless-wsgi`) ready for 1-click cloud deployment.

---

## 📁 Directory Structure

```
pdf_automation/
├── netlify/
│   └── functions/
│       └── app.py               # Netlify Serverless Python WSGI handler
├── templates/
│   ├── offer_letter.html        # Jinja2 template for Offer Letters
│   └── certificate.html         # Jinja2 template for Certificates of Completion
├── public/
│   └── index.html               # Netlify static fallback publish folder
├── generator.py                 # Core Jinja2 render & multi-backend PDF conversion engine
├── cli.py                       # CLI tool for single execution, interactive mode & batch CSV processing
├── app.py                       # Modern Flask Web Dashboard & REST API
├── netlify.toml                 # Netlify serverless build & routing configuration
├── requirements.txt             # Python dependencies for Netlify deployment
├── NETLIFY_DEPLOYMENT.md        # Complete Netlify step-by-step deployment guide
└── README.md                    # System documentation
```


---

## 🚀 How to Run

### 1. Python Automation Engine (`generator.py`)

Run the core automation script to test single document rendering for both Offer Letter and Certificate:

```bash
python generator.py
```

Generated files will be saved in `pdf_automation/output/`:
- `Offer_Letter_Jane_Doe.pdf`
- `Certificate_Sayaji_Kapse.pdf`

---

### 2. Batch Processing from CSV (`cli.py`)

To generate multiple PDFs in bulk from a CSV file (such as `sample_batch.csv`):

```bash
# Generate Certificates for all rows in CSV
python cli.py --csv sample_batch.csv --template certificate

# Generate Offer Letters for all rows in CSV
python cli.py --csv sample_batch.csv --template offer_letter
```

### 3. Interactive CLI Mode

Run step-by-step interactive CLI prompts:

```bash
python cli.py --interactive
```

---

### 4. Interactive Web Dashboard (`app.py`)

Start the web studio app on `http://127.0.0.1:5000`:

```bash
python app.py
```

Then open `http://127.0.0.1:5000` in your web browser to fill out fields, preview HTML live, and download PDFs directly.

---

## 📝 Example Python Usage

```python
from datetime import datetime
from generator import generate_document

# Define dynamic data
data = {
    "name": "Jane Doe",
    "role": "Senior Full-Stack Developer",
    "duration": "24 Months",
    "serial_no": "KT-2026-08-001",
    "date": datetime.today().strftime('%B %d, %Y'),
    "company_name": "Kalki Technology Pvt. Ltd.",
    "holding_company": "Neeta Holdings Pvt. Ltd."
}

# Generate PDF
generate_document("templates/offer_letter.html", data, "output/Offer_Letter_Jane_Doe.pdf")
```
