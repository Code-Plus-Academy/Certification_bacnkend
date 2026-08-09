# 🚀 Netlify Deployment Guide for PDF Automation Studio

This project is fully configured for deployment on **Netlify** using **Netlify Serverless Python Functions** (`serverless-wsgi`).

---

## 🏗️ How It Works on Netlify

Netlify hosts the Flask web application as a serverless microservice using AWS Lambda under the hood.

- **Routing**: `netlify.toml` redirects all incoming web traffic (`/*`) to the Netlify Serverless Function `/.netlify/functions/app`.
- **WSGI Bridge**: `netlify/functions/app.py` wraps the Flask `app` object using `serverless_wsgi`.
- **Filesystem & PDF Engine**: Serverless Linux containers have a read-only root filesystem. The application automatically redirects dynamic PDF outputs and custom templates to `/tmp`. PDF conversion seamlessly uses `xhtml2pdf` (pure Python) on Linux serverless environments.

---

## ⚡ Deployment Options

### Method 1: Deploying via Netlify CLI (Recommended)

1. **Install Netlify CLI** (if not already installed):
   ```bash
   npm install -g netlify-cli
   ```

2. **Log in to Netlify**:
   ```bash
   netlify login
   ```

3. **Initialize the Project**:
   ```bash
   netlify init
   ```
   - Choose **Create & configure a new site**.
   - Select your Netlify team.
   - Enter a site name (e.g. `pdf-automation-studio`).
   - Build settings will automatically load from `netlify.toml`.

4. **Deploy to Production**:
   ```bash
   netlify deploy --prod
   ```

---

### Method 2: Deploying via GitHub / Git Integration (Automated CI/CD)

1. Push your project to a GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Configure PDF Automation Studio for Netlify"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/pdf_automation.git
   git push -u origin main
   ```

2. Log in to [Netlify Dashboard](https://app.netlify.com/).
3. Click **Add new site** -> **Import an existing project**.
4. Connect to **GitHub** and select your `pdf_automation` repository.
5. Netlify will auto-detect configurations from `netlify.toml`:
   - **Build command**: `pip install -r requirements.txt`
   - **Publish directory**: `public`
   - **Functions directory**: `netlify/functions`
6. Click **Deploy site**.

---

## 🔐 Environment Variables (Optional Cloud Uploaders)

If you use external cloud storage features (Supabase, AWS S3, or Cloudinary), add these environment variables in **Netlify Dashboard -> Site settings -> Environment variables**:

### Supabase Storage
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-key
```

### AWS S3 Storage
```env
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
```

### Cloudinary
```env
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

---

## 🧪 Testing Live Endpoints

Once deployed, test your live Netlify site URL (e.g., `https://your-site.netlify.app`):

1. **Web Dashboard**: Navigate to `https://your-site.netlify.app/`
2. **List Templates API**: `GET https://your-site.netlify.app/api/templates`
3. **Generate Certificate Info API**: `POST https://your-site.netlify.app/api/generate-certificate-info`
   - Body JSON:
     ```json
     {
       "template": "certificate.html",
       "data": {
         "name": "Jane Doe",
         "role": "Full-Stack Developer",
         "organization_name": "Code Plus Academy"
       }
     }
     ```
