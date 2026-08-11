# 📜 PolyCert — Enterprise HTML Templating & PDF Generation Engine
## Complete API & Integration Documentation

Welcome to the official integration guide for **PolyCert**, an enterprise-grade automated PDF generation and HTML templating engine. **PolyCert** leverages **Playwright Chromium** to render dynamic HTML/CSS templates into pixel-perfect PDF documents, with automatic cloud storage uploads to **Supabase Storage**, **Cloudinary**, and **AWS S3**.

---

## 📍 Service Endpoints & Base URLs

| Environment | Base URL | Status / Notes |
| :--- | :--- | :--- |
| **Production API (Render)** | `https://certification-bacnkend.onrender.com` | High-availability Playwright Chromium backend |
| **Netlify Serverless** | `https://certification-cpa.netlify.app` | Serverless WSGI endpoint |
| **Local Development** | `http://127.0.0.1:5000` | Local Flask development server |

---

## 🔒 1. Security & Authentication

PolyCert uses two distinct authentication layers:

### A. REST API Key Authentication (`/api/*`)
All programmatic API endpoints starting with `/api/` require a valid **Server Access Key**. You can pass your key using any of the following 3 header/parameter formats:

| Method | Type | Header / Parameter | Example |
| :--- | :--- | :--- | :--- |
| **HTTP Header (Recommended)** | `X-API-Key` | Header | `X-API-Key: cpa_sk_89f2a71e4b9d0831` |
| **Authorization Header** | `Authorization` | Bearer Token | `Authorization: Bearer cpa_sk_89f2a71e4b9d0831` |
| **Query Parameter** | `api_key` | URL Parameter | `?api_key=cpa_sk_89f2a71e4b9d0831` |

> ⚠️ **Unauthorized API Response (401)**:
> ```json
> {
>   "status": "error",
>   "error": "Unauthorized: Invalid or missing API access key",
>   "message": "Please provide your server access key via 'X-API-Key' header or 'Authorization: Bearer <key>'"
> }
> ```

---

### B. Web Studio Dashboard Authentication (`/login`)
The interactive Web Dashboard (`http://127.0.0.1:5000/`) is protected by **Flask Session Authentication**:
- **Automatic Redirect**: Accessing any dashboard URL without an active session redirects to `/login`.
- **Admin Password**: Enter your `API_ACCESS_KEY` (`cpa_sk_89f2a71e4b9d0831`) in the login form to unlock full dashboard access.
- **Logout**: Click **🔒 Logout** in the navigation header or request `/logout` to clear your active session.

---

## 📑 2. API Endpoints Quick Reference

| Category | HTTP Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/health` / `/ping` | Lightweight zero-overhead keep-alive & health check |
| **Auth** | `POST` | `/login` | Authenticate web session using Access Key |
| **Auth** | `GET` | `/logout` | End web session and redirect to `/login` |
| **Templates** | `GET` | `/api/templates` | List all installed templates & Jinja2 variables |
| **Templates** | `GET` | `/api/templates/<filename>` | Retrieve raw HTML and variables for a template |
| **Templates** | `POST` | `/api/templates` | Create or update a custom HTML template |
| **Templates** | `DELETE` | `/api/templates/<filename>` | Delete a custom template |
| **Generation** | `POST` | `/api/generate-certificate-info` | Generate single PDF + JSON metadata + Cloud storage links |
| **Generation** | `POST` | `/api/generate-batch-info` | Generate bulk PDFs returning JSON array with cloud URLs |
| **Generation** | `POST` | `/api/generate-batch-pdf` | Generate bulk PDFs returning a `.zip` archive download |
| **Download** | `GET` | `/output/<filename>` | Download a generated PDF file from server |

---

## 📂 3. Template Management API

### `GET /api/templates`
Retrieves a list of all installed templates along with their auto-detected Jinja2 `{{ variable }}` placeholders.

#### Request Headers:
```http
X-API-Key: cpa_sk_89f2a71e4b9d0831
```

#### Response (200 OK):
```json
{
  "status": "success",
  "templates": [
    {
      "filename": "certificate_of_compleation.html",
      "is_custom": false,
      "name": "Certificate Of Compleation",
      "path": "/opt/render/project/src/templates/certificate_of_compleation.html",
      "variables": [
        "date",
        "duration",
        "name",
        "organization_name",
        "program_lead",
        "program_lead_org",
        "program_lead_title",
        "role",
        "serial_no",
        "signatory",
        "signatory_role"
      ]
    },
    {
      "filename": "offer_letter.html",
      "is_custom": false,
      "name": "Offer Letter",
      "path": "/opt/render/project/src/templates/offer_letter.html",
      "variables": [
        "company_name",
        "date",
        "duration",
        "holding_company",
        "name",
        "role",
        "serial_no",
        "signatory",
        "signatory_role",
        "signature_image",
        "signature_text"
      ]
    }
  ]
}
```

---

### `GET /api/templates/<filename>`
Retrieves raw HTML content and Jinja2 variables for a specific template.

#### Request Example:
```http
GET /api/templates/certificate_of_compleation.html
X-API-Key: cpa_sk_89f2a71e4b9d0831
```

#### Response (200 OK):
```json
{
  "status": "success",
  "filename": "certificate_of_compleation.html",
  "variables": ["date", "duration", "name", "organization_name", "role", "serial_no"],
  "html_content": "<!DOCTYPE html><html>..."
}
```

---

### `POST /api/templates`
Creates or updates a custom HTML Jinja2 template.

#### Request Body (JSON):
```json
{
  "name": "internship_certificate",
  "html": "<html><body><h1>Internship Certificate</h1><p>Awarded to {{ name }} for completing {{ role }}.</p></body></html>"
}
```

#### Response (201 Created):
```json
{
  "status": "success",
  "message": "Template 'internship_certificate.html' saved successfully",
  "filename": "internship_certificate.html",
  "variables": ["name", "role"]
}
```

---

### `DELETE /api/templates/<filename>`
Deletes a custom HTML template.

#### Request Example:
```http
DELETE /api/templates/internship_certificate.html
X-API-Key: cpa_sk_89f2a71e4b9d0831
```

#### Response (200 OK):
```json
{
  "status": "success",
  "message": "Template 'internship_certificate.html' deleted successfully"
}
```

---

## 🖨️ 4. PDF Generation Endpoints

### `POST /api/generate-certificate-info` (Primary Single Document API)
Renders a PDF using **Playwright Chromium**, returns structured JSON metadata, and automatically uploads the generated file to **Supabase Storage** CDN.

#### Request Headers:
```http
Content-Type: application/json
X-API-Key: cpa_sk_89f2a71e4b9d0831
```

#### Request Body Payload (JSON):
```json
{
  "template": "certificate_of_compleation.html",
  "data": {
    "name": "Sayaji Kapse",
    "role": "Senior Software Engineer & AI Specialist",
    "organization_name": "Code Plus Academy",
    "duration": "120 Hours",
    "serial_no": "POLYCERT-2026-SK-001",
    "date": "August 10, 2026",
    "signatory": "Dr. Alex Vance",
    "signatory_role": "Director of Engineering",
    "signature_text": "Dr. Alex Vance",
    "program_lead": "Dr. Alex Vance",
    "program_lead_title": "Director of Engineering",
    "program_lead_org": "Code Plus Academy"
  }
}
```

#### Response (200 OK):
```json
{
  "status": "success",
  "request_id": "req_77f641f6-6059",
  "certificate_serial": "POLYCERT-2026-SK-001",
  "recipient_name": "Sayaji Kapse",
  "role_title": "Senior Software Engineer & AI Specialist",
  "template_used": "certificate_of_compleation.html",
  "generated_at": "2026-08-10T00:20:00.123456",
  "file_info": {
    "filename": "cert_POLYCERT-2026-SK-001_Sayaji_Kapse.pdf",
    "size_bytes": 612073,
    "local_download_url": "https://certification-bacnkend.onrender.com/output/cert_POLYCERT-2026-SK-001_Sayaji_Kapse.pdf"
  },
  "cloud_storage_urls": {
    "local_download_url": "https://certification-bacnkend.onrender.com/output/cert_POLYCERT-2026-SK-001_Sayaji_Kapse.pdf",
    "supabase_url": "https://hbgclryfeuixuynnilqa.supabase.co/storage/v1/object/public/certificates/certificates/2026/08/cert_POLYCERT-2026-SK-001_Sayaji_Kapse.pdf"
  }
}
```

---

### ✍️ Digital Signature Modes
PolyCert supports 3 digital signature formats inside the `data` object:

1. **Stylized Cursive Signature (`signature_text`)**:
   Renders a handwritten signature using Google Font *Dancing Script*:
   ```json
   { "signature_text": "Dr. Alex Vance" }
   ```

2. **Image URL (`signature_image`)**:
   Pass a remote PNG/SVG image URL:
   ```json
   { "signature_image": "https://yourdomain.com/assets/signature.png" }
   ```

3. **Base64 Data URI (`signature_image`)**:
   Pass inline base64 image data:
   ```json
   { "signature_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..." }
   ```

---

### `POST /api/generate-batch-info` (Bulk Generation API)
Generates multiple PDFs from an array of data objects and returns a JSON list of all generated documents with individual cloud storage URLs.

#### Request Body Payload:
```json
{
  "template": "certificate_of_compleation.html",
  "data_list": [
    {
      "name": "Jane Doe",
      "role": "Full-Stack Engineer",
      "serial_no": "POLYCERT-BATCH-001"
    },
    {
      "name": "Alex Mercer",
      "role": "DevOps Architect",
      "serial_no": "POLYCERT-BATCH-002"
    }
  ]
}
```

#### Response (200 OK):
```json
{
  "status": "success",
  "batch_id": "batch_98f7e6d5c4b3a",
  "total_generated": 2,
  "certificates": [
    {
      "certificate_serial": "POLYCERT-BATCH-001",
      "recipient_name": "Jane Doe",
      "cloud_storage_urls": {
        "supabase_url": "https://hbgclryfeuixuynnilqa.supabase.co/storage/v1/object/public/certificates/certificates/2026/08/batch_POLYCERT-BATCH-001_Jane_Doe.pdf"
      }
    },
    {
      "certificate_serial": "POLYCERT-BATCH-002",
      "recipient_name": "Alex Mercer",
      "cloud_storage_urls": {
        "supabase_url": "https://hbgclryfeuixuynnilqa.supabase.co/storage/v1/object/public/certificates/certificates/2026/08/batch_POLYCERT-BATCH-002_Alex_Mercer.pdf"
      }
    }
  ]
}
```

---

### `POST /api/generate-batch-pdf` (ZIP File Download)
Generates multiple PDFs and returns a single downloadable `.zip` archive containing all generated PDF files.

#### Request Body Payload:
```json
{
  "template": "offer_letter.html",
  "data_list": [
    { "name": "User A", "role": "Developer" },
    { "name": "User B", "role": "Designer" }
  ]
}
```

#### Response:
- **Content-Type**: `application/zip`
- **File Download**: `Batch_offer_letter_20260810_002000.zip`

---

## 💻 5. Integration Code Examples

### 1. cURL (Command Line)
```bash
curl -X POST https://certification-bacnkend.onrender.com/api/generate-certificate-info \
  -H "X-API-Key: cpa_sk_89f2a71e4b9d0831" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "certificate_of_compleation.html",
    "data": {
      "name": "Sayaji Kapse",
      "role": "Senior Software Engineer & AI Specialist",
      "serial_no": "POLYCERT-CURL-01",
      "signature_text": "Dr. Alex Vance"
    }
  }'
```

---

### 2. JavaScript / Node.js (Fetch API)
```javascript
const BASE_URL = "https://certification-bacnkend.onrender.com";
const API_KEY = "cpa_sk_89f2a71e4b9d0831";

async function generatePolyCert(studentData) {
  const response = await fetch(`${BASE_URL}/api/generate-certificate-info`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY
    },
    body: JSON.stringify({
      template: "certificate_of_compleation.html",
      data: studentData
    })
  });

  const result = await response.json();
  if (response.ok) {
    console.log("Certificate Generated Successfully!");
    console.log("Supabase CDN URL:", result.cloud_storage_urls.supabase_url);
    return result.cloud_storage_urls.supabase_url;
  } else {
    console.error("PolyCert Error:", result.error);
  }
}

// Call service
generatePolyCert({
  name: "Sayaji Kapse",
  role: "Senior Software Engineer & AI Specialist",
  signature_text: "Dr. Alex Vance",
  serial_no: "POLYCERT-JS-01"
});
```

---

### 3. React / Next.js Frontend Integration
```tsx
import React, { useState } from "react";

export default function CertificateGenerator() {
  const [loading, setLoading] = useState(false);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await fetch("https://certification-bacnkend.onrender.com/api/generate-certificate-info", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": "cpa_sk_89f2a71e4b9d0831"
        },
        body: JSON.stringify({
          template: "certificate_of_compleation.html",
          data: {
            name: "Sayaji Kapse",
            role: "Senior Full-Stack & AI Engineer",
            serial_no: `POLYCERT-${Date.now()}`
          }
        })
      });

      const data = await res.json();
      if (res.ok) {
        setPdfUrl(data.cloud_storage_urls.supabase_url);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? "Generating PolyCert PDF..." : "Generate Certificate"}
      </button>

      {pdfUrl && (
        <div style={{ marginTop: "20px" }}>
          <p>Certificate Ready!</p>
          <a href={pdfUrl} target="_blank" rel="noreferrer">
            View / Download PDF (Supabase CDN)
          </a>
        </div>
      )}
    </div>
  );
}
```

---

### 4. Python (`requests`)
```python
import requests

url = "https://certification-bacnkend.onrender.com/api/generate-certificate-info"
headers = {
    "X-API-Key": "cpa_sk_89f2a71e4b9d0831",
    "Content-Type": "application/json"
}

payload = {
    "template": "certificate_of_compleation.html",
    "data": {
        "name": "Sayaji Kapse",
        "role": "Senior Software Engineer & AI Specialist",
        "signature_text": "Dr. Alex Vance",
        "serial_no": "POLYCERT-PY-01"
    }
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()

print("Status Code:", response.status_code)
print("Supabase CDN URL:", data["cloud_storage_urls"]["supabase_url"])
```

---

### 5. PHP (cURL)
```php
<?php
$url = "https://certification-bacnkend.onrender.com/api/generate-certificate-info";
$apiKey = "cpa_sk_89f2a71e4b9d0831";

$payload = [
    "template" => "certificate_of_compleation.html",
    "data" => [
        "name" => "Sayaji Kapse",
        "role" => "Senior Software Engineer & AI Specialist",
        "signature_text" => "Dr. Alex Vance",
        "serial_no" => "POLYCERT-PHP-01"
    ]
];

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    "Content-Type: application/json",
    "X-API-Key: " . $apiKey
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));

$response = curl_exec($ch);
curl_close($ch);

$result = json_decode($response, true);
echo "Supabase Link: " . $result['cloud_storage_urls']['supabase_url'];
?>
```

---

## ⚙️ 6. Environment Variables Reference

Configure these variables in your `.env` file or host environment (Render / Netlify):

```env
# 🔑 API & Admin Authentication
API_ACCESS_KEY=cpa_sk_89f2a71e4b9d0831

# ⚡ Supabase Storage Ingestion
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SECRET_KEY=your_supabase_secret_key
SUPABASE_BUCKET=certificates

# ☁️ Cloudinary (Optional)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# 📦 AWS S3 Storage (Optional)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
```
