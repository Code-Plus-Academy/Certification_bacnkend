# HTML Template Structure & Jinja2 Guidelines for PDF Generation

To ensure your custom HTML drafts convert into **pixel-perfect PDFs** (for certificates, offer letters, or official credentials), your HTML draft must follow the structural guidelines below.

---

## 📌 1. Jinja2 Placeholder Syntax

Dynamic variables in your HTML draft must be wrapped using standard Jinja2 syntax:

### Basic Variable
```html
<p>Dear <strong>{{ name }}</strong>,</p>
<p>Subject: Offer of Employment - {{ role }}</p>
```

### Variable with Default Fallback Value
```html
<h1>{{ company_name | default('Code Plus Academy') }}</h1>
```

### Conditional Statements
```html
{% if honors %}
  <div class="badge">Passed with Distinction</div>
{% endif %}
```

> **Note**: Our system automatically parses your HTML template, detects all `{{ placeholder }}` variables, and generates UI input forms for them automatically!

---

## 📐 2. Page Dimensions & CSS `@page` Rules

Always declare `@page` dimensions in your `<style>` block so the PDF engine sets exact paper boundaries.

### A. For Offer Letters (A4 Portrait)
```css
@page {
    size: A4 portrait;
    margin: 20mm; /* Standard document margins */
    background-color: #ffffff;
}

body {
    font-family: 'Helvetica', 'Arial', sans-serif;
    color: #333333;
    line-height: 1.6;
}
```

### B. For Certificates (A4 Landscape)
```css
@page {
    size: 297mm 210mm; /* A4 Landscape Dimensions */
    margin: 0;         /* Borderless layout for background artwork */
}

body {
    margin: 0;
    padding: 0;
    font-family: 'Inter', sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
}

.sheet {
    width: 297mm;
    height: 210mm;
    position: relative;
    overflow: hidden;
    background: #ffffff;
    display: flex;
}
```

---

## 🎨 3. Styling Best Practices

1. **Modern CSS Layouts**:
   - Flexbox (`display: flex; flex-direction: column; justify-content: space-between;`) and Grid (`display: grid;`) are fully supported by our Headless Browser rendering engine.
2. **Typography & Fonts**:
   - Include Google Fonts via standard `<link>` tags in the `<head>`:
     ```html
     <link rel="preconnect" href="https://fonts.googleapis.com">
     <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
     ```
3. **Gradients & Colors**:
   - Standard CSS linear & radial gradients are supported:
     ```css
     background: linear-gradient(90deg, #1EC8F0, #2F6DF6, #8B3DF5);
     ```

---

## 🖼️ 4. Including Logos, Badges & Signatures

- **Inline Base64 Images** (Recommended for portability):
  ```html
  <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..." alt="Logo" />
  ```
- **Local File Images**:
  ```html
  <img src="assets/logo.png" alt="Company Logo" />
  ```
- **SVG Badges**:
  ```html
  <svg width="60" height="60">...</svg>
  ```

---

## 🖨️ 5. Print Media CSS Rules

Include print media reset rules at the bottom of your `<style>` block:

```css
@media print {
    body { background: none; padding: 0; }
    .sheet { box-shadow: none; }
    @page { margin: 0; }
}
```

---

## 📋 6. Full Minimal Custom Offer Letter Template Example

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Offer Letter - {{ name }}</title>
<style>
  @page { size: A4 portrait; margin: 20mm; }
  body { font-family: Arial, sans-serif; color: #222; line-height: 1.6; }
  .header { text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-bottom: 30px; }
  .company { font-size: 24pt; font-weight: bold; color: #2c3e50; }
  .meta { display: flex; justify-content: space-between; margin-bottom: 25px; }
  .subject { font-weight: bold; text-decoration: underline; margin-bottom: 20px; }
</style>
</head>
<body>
  <div class="header">
    <div class="company">{{ company_name }}</div>
    <p>A Subsidiary of {{ holding_company }}</p>
  </div>

  <div class="meta">
    <div><strong>Ref No:</strong> {{ serial_no }}</div>
    <div><strong>Date:</strong> {{ date }}</div>
  </div>

  <p>Dear <strong>{{ name }}</strong>,</p>

  <div class="subject">Subject: Offer of Employment - {{ role }}</div>

  <p>We are pleased to offer you the position of <strong>{{ role }}</strong> at {{ company_name }} for a duration of <strong>{{ duration }}</strong>.</p>

  <div style="margin-top: 60px;">
    <p>Sincerely,</p>
    <br><br>
    <strong>Authorized Signatory</strong><br>
    {{ company_name }}
  </div>
</body>
</html>
```

---

## 🎓 7. Full Minimal Custom Certificate Template Example

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Certificate of Completion</title>
<style>
  @page { size: 297mm 210mm; margin: 0; }
  body { margin: 0; font-family: Arial, sans-serif; background: #0E1220; color: #FFF; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
  .sheet { width: 297mm; height: 210mm; padding: 20mm; box-sizing: border-box; text-align: center; border: 10px solid #2F6DF6; }
  h1 { font-size: 36pt; color: #1EC8F0; }
  .name { font-size: 42pt; font-weight: bold; color: #FFF; border-bottom: 3px solid #8B3DF5; display: inline-block; margin: 20px 0; }
</style>
</head>
<body>
  <div class="sheet">
    <h1>CERTIFICATE OF ACHIEVEMENT</h1>
    <p>THIS IS PROUDLY PRESENTED TO</p>
    <div class="name">{{ name }}</div>
    <p>For successfully completing <strong>{{ role }}</strong> at {{ organization_name }}.</p>
    <div style="margin-top: 40px; display: flex; justify-content: space-between;">
      <div>ID: {{ serial_no }}</div>
      <div>Date: {{ date }}</div>
      <div>Issued By: {{ signatory }}</div>
    </div>
  </div>
</body>
</html>
```
