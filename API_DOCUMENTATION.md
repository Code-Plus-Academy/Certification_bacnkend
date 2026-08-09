# 📘 Certification Backend & PDF Automation Studio — Complete API Documentation

Comprehensive API documentation for the **PDF Automation & Templating System**. This backend enables dynamic HTML Jinja2 template management, digital signature rendering, single and batch PDF generation, and automated cloud storage uploads to **Supabase**, **Cloudinary**, and **AWS S3**.

---

## 📍 Base URLs

- **Production API (Render)**: `https://certification-bacnkend.onrender.com`
- **Netlify Serverless**: `https://certification-cpa.netlify.app`
- **Local Development**: `http://127.0.0.1:5000`

---

## 🔑 Authentication

All `/api/` endpoints are protected by an **API Access Key**. You must supply your key using any of the following 3 methods:

| Method | Type | Format | Example |
| :--- | :--- | :--- | :--- |
| **HTTP Header (Recommended)** | `X-API-Key` | Plain String | `X-API-Key: cpa_sk_89f2a71e4b9d0831` |
| **Authorization Header** | `Authorization` | Bearer Token | `Authorization: Bearer cpa_sk_89f2a71e4b9d0831` |
| **Query Parameter** | `api_key` | URL Parameter | `?api_key=cpa_sk_89f2a71e4b9d0831` |

> ⚠️ **Unauthorized Response (401)**: If a request lacks a valid key, the API returns:
> ```json
> {
>   "status": "error",
>   "error": "Unauthorized: Invalid or missing API access key",
>   "message": "Please provide your server access key via 'X-API-Key' header or 'Authorization: Bearer <key>'"
> }
> ```

---

### 🔒 Frontend Web Dashboard Authentication (`/login`)
The PolyCert Studio Web Dashboard (`/`) is protected by **Session Authentication**:
- **Login Redirect**: Accessing any dashboard route (`/`, `/?tab=templates`) without an active session automatically redirects to `/login`.
- **Authentication Key**: Enter your **Server Access Key** (`API_ACCESS_KEY=cpa_sk_89f2a71e4b9d0831`) in the dark-mode login card to authenticate.
- **Logout**: Click **🔒 Logout** in the navigation header or navigate to `/logout` to clear your active session.

---

## 📑 Quick Reference Table

| Category | HTTP Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Templates** | `GET` | `/api/templates` | List all installed templates & Jinja2 variables |
| **Templates** | `GET` | `/api/templates/<filename>` | Get raw HTML & detected placeholders for a template |
| **Templates** | `POST` / `PUT` | `/api/templates` | Create or update a custom HTML template via API |
| **Templates** | `DELETE` | `/api/templates/<filename>` | Delete a custom HTML template |
| **Generation** | `POST` | `/api/generate-certificate-info` | Single PDF generation + JSON metadata + Cloud storage links |
| **Generation** | `POST` | `/api/generate-batch-info` | Bulk PDF generation returning JSON array with cloud URLs |
| **Generation** | `POST` | `/api/generate-batch-pdf` | Bulk PDF generation returning a `.zip` archive download |
| **Download** | `GET` | `/output/<filename>` | Download a generated PDF file from server |

---

## 📂 1. Template Management Endpoints

### `GET /api/templates`
Returns a list of all installed templates along with their auto-detected Jinja2 `{{ variable }}` placeholders.

#### Request Header:
```http
X-API-Key: cpa_sk_89f2a71e4b9d0831
```

#### Response (200 OK):
```json
{
  "status": "success",
  "templates": [
    {
      "filename": "certificate.html",
      "is_custom": false,
      "name": "Certificate",
      "path": "/opt/render/project/src/templates/certificate.html",
      "variables": [
        "date",
        "doc_tag",
        "duration",
        "eyebrow",
        "holding_company",
        "name",
        "organization_name",
        "role",
        "serial_no",
        "signatory",
        "signatory_role",
        "signature_image",
        "signature_text"
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
Returns the raw HTML content and variables for a specific template.

#### Request Example:
```http
GET /api/templates/certificate.html
X-API-Key: cpa_sk_89f2a71e4b9d0831
```

#### Response (200 OK):
```json
{
  "status": "success",
  "filename": "certificate.html",
  "variables": ["date", "name", "role", "serial_no", "signature_text"],
  "html_content": "<!DOCTYPE html><html>..."
}
```

---

### `POST /api/templates`
Creates or updates a custom HTML template. The system automatically validates Jinja2 syntax and extracts variable placeholders.

#### Request Body (JSON):
```json
{
  "name": "internship_letter",
  "html": "<html><body><h1>Internship Certificate</h1><p>Awarded to {{ name }} for completing {{ role }}. Signed by {{ signatory }}.</p></body></html>"
}
```

#### Response (201 Created):
```json
{
  "status": "success",
  "message": "Template 'internship_letter.html' saved successfully",
  "filename": "internship_letter.html",
  "variables": [
    "name",
    "role",
    "signatory"
  ]
}
```

---

### `DELETE /api/templates/<filename>`
Deletes a custom HTML template.

#### Request Example:
```http
DELETE /api/templates/internship_letter.html
X-API-Key: cpa_sk_89f2a71e4b9d0831
```

#### Response (200 OK):
```json
{
  "status": "success",
  "message": "Template 'internship_letter.html' deleted successfully"
}
```

---

## 🖨️ 2. PDF Generation Endpoints

### `POST /api/generate-certificate-info` (Primary Single Document API)
Generates a PDF document, returns detailed JSON metadata, and automatically uploads the generated file to your enabled cloud storage providers (**Supabase**, **Cloudinary**, **AWS S3**).

#### Request Headers:
```http
Content-Type: application/json
X-API-Key: cpa_sk_89f2a71e4b9d0831
```

#### Request Body Payload (JSON):
```json
{
  "template": "certificate.html",
  "data": {
    "name": "Sayaji Kapse",
    "role": "Lead Software & AI Engineer",
    "organization_name": "Code Plus Academy",
    "duration": "120 Hours",
    "serial_no": "CERT-2026-SK-8891",
    "date": "August 09, 2026",
    "signatory": "Dr. Alex Vance",
    "signatory_role": "Director of Engineering",
    "signature_text": "Dr. Alex Vance"
  }
}
```

#### Response (200 OK):
```json
{
  "status": "success",
  "request_id": "req_a1b2c3d4e5f67",
  "certificate_serial": "CERT-2026-SK-8891",
  "recipient_name": "Sayaji Kapse",
  "role_title": "Lead Software & AI Engineer",
  "template_used": "certificate.html",
  "generated_at": "2026-08-09T17:19:17.522211",
  "file_info": {
    "filename": "cert_CERT-2026-SK-8891_Sayaji_Kapse.pdf",
    "size_bytes": 45917,
    "local_download_url": "https://certification-bacnkend.onrender.com/output/cert_CERT-2026-SK-8891_Sayaji_Kapse.pdf"
  },
  "cloud_storage_urls": {
    "local_download_url": "https://certification-bacnkend.onrender.com/output/cert_CERT-2026-SK-8891_Sayaji_Kapse.pdf",
    "supabase_url": "https://hbgclryfeuixuynnilqa.supabase.co/storage/v1/object/public/certificates/certificates/2026/08/cert_CERT-2026-SK-8891_Sayaji_Kapse.pdf"
  }
}
```

---

### ✍️ Digital Signature Features

You can provide signatures in three ways inside the `data` payload:

#### 1. Stylized Cursive Signature (`signature_text`)
Pass `signature_text` to automatically render an elegant handwritten cursive script signature:
```json
{
  "signature_text": "Dr. Alex Vance",
  "signatory": "Dr. Alex Vance",
  "signatory_role": "Director of Engineering"
}
```

#### 2. Signature Image URL (`signature_image`)
Pass an image URL or relative server path:
```json
{
  "signature_image": "https://yourdomain.com/assets/signature.png",
  "signatory": "Dr. Alex Vance"
}
```

#### 3. Base64 Data URI (`signature_image`)
Pass inline base64 image data:
```json
{
  "signature_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "signatory": "Dr. Alex Vance"
}
```

---

### `POST /api/generate-batch-info` (Bulk JSON Generation)
Generates multiple PDFs for an array of records and returns a JSON list of all generated documents with individual download and cloud storage links.

#### Request Body Payload:
```json
{
  "template": "certificate.html",
  "data_list": [
    {
      "name": "Jane Doe",
      "role": "Full-Stack Developer",
      "serial_no": "CPA-2026-001"
    },
    {
      "name": "Alex Mercer",
      "role": "DevOps Architect",
      "serial_no": "CPA-2026-002"
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
  "generated_at": "2026-08-09T17:20:00.123456",
  "certificates": [
    {
      "request_id": "req_11111111",
      "certificate_serial": "CPA-2026-001",
      "recipient_name": "Jane Doe",
      "role_title": "Full-Stack Developer",
      "file_info": {
        "filename": "batch_CPA-2026-001_Jane_Doe.pdf",
        "size_bytes": 44810,
        "local_download_url": "https://certification-bacnkend.onrender.com/output/batch_CPA-2026-001_Jane_Doe.pdf"
      },
      "cloud_storage_urls": {
        "supabase_url": "https://hbgclryfeuixuynnilqa.supabase.co/storage/v1/object/public/certificates/certificates/2026/08/batch_CPA-2026-001_Jane_Doe.pdf"
      }
    },
    {
      "request_id": "req_22222222",
      "certificate_serial": "CPA-2026-002",
      "recipient_name": "Alex Mercer",
      "role_title": "DevOps Architect",
      "file_info": {
        "filename": "batch_CPA-2026-002_Alex_Mercer.pdf",
        "size_bytes": 45120,
        "local_download_url": "https://certification-bacnkend.onrender.com/output/batch_CPA-2026-002_Alex_Mercer.pdf"
      },
      "cloud_storage_urls": {
        "supabase_url": "https://hbgclryfeuixuynnilqa.supabase.co/storage/v1/object/public/certificates/certificates/2026/08/batch_CPA-2026-002_Alex_Mercer.pdf"
      }
    }
  ]
}
```

---

### `POST /api/generate-batch-pdf` (ZIP Archive Download)
Generates multiple PDFs and returns a single `.zip` file containing all generated PDF files as an attachment.

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
- **File Download**: `Batch_offer_letter_20260809_172000.zip`

---

## 💻 3. Integration Code Examples

### 1. cURL (Command Line)
```bash
curl -X POST https://certification-bacnkend.onrender.com/api/generate-certificate-info \
  -H "X-API-Key: cpa_sk_89f2a71e4b9d0831" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "certificate.html",
    "data": {
      "name": "Jane Doe",
      "role": "Full-Stack Engineer",
      "serial_no": "CERT-2026-101",
      "signature_text": "Dr. Alex Vance"
    }
  }'
```

---

### 2. JavaScript / Node.js (Fetch API)
```javascript
const BASE_URL = "https://certification-bacnkend.onrender.com";
const API_KEY = "cpa_sk_89f2a71e4b9d0831";

async function generateCertificate(candidateData) {
  const response = await fetch(`${BASE_URL}/api/generate-certificate-info`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY
    },
    body: JSON.stringify({
      template: "certificate.html",
      data: candidateData
    })
  });

  const result = await response.json();
  if (response.ok) {
    console.log("Certificate Generated Successfully!");
    console.log("Supabase CDN URL:", result.cloud_storage_urls.supabase_url);
    return result;
  } else {
    console.error("API Error:", result.error);
  }
}

// Call function
generateCertificate({
  name: "Sayaji Kapse",
  role: "Lead Software Engineer",
  signature_text: "Dr. Alex Vance",
  serial_no: "CERT-2026-99"
});
```

---

### 3. Python (`requests`)
```python
import requests

BASE_URL = "https://certification-bacnkend.onrender.com"
API_KEY = "cpa_sk_89f2a71e4b9d0831"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "template": "certificate.html",
    "data": {
        "name": "Sayaji Kapse",
        "role": "AI Engineer",
        "signature_text": "Dr. Alex Vance",
        "serial_no": "CPA-2026-PY-01"
    }
}

response = requests.post(f"{BASE_URL}/api/generate-certificate-info", headers=headers, json=payload)
data = response.json()

print("Status Code:", response.status_code)
print("Supabase CDN Link:", data["cloud_storage_urls"]["supabase_url"])
```

---

### 4. PHP (cURL)
```php
<?php
$url = "https://certification-bacnkend.onrender.com/api/generate-certificate-info";
$apiKey = "cpa_sk_89f2a71e4b9d0831";

$payload = [
    "template" => "certificate.html",
    "data" => [
        "name" => "Sayaji Kapse",
        "role" => "Lead Engineer",
        "signature_text" => "Dr. Alex Vance"
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

## ⚙️ 4. Environment Variables Reference

Configure these variables in your `.env` or host environment (Render / Netlify):

```env
# 🔑 API Authentication
API_ACCESS_KEY=cpa_sk_89f2a71e4b9d0831

# ⚡ Supabase Storage
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
