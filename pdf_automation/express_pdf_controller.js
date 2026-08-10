/**
 * Express.js PDF & Certificate Automation Router/Controller
 * 
 * Provides full control functionality from your main Express backend:
 * - List all installed HTML templates & Jinja2 placeholders
 * - Upload / Create / Modify custom HTML templates
 * - Delete custom HTML templates
 * - Generate specific single PDF certificates / offer letters (Binary stream OR Structured JSON with Cloud URLs)
 * - Bulk/Batch PDF generation returning ZIP archive OR Structured JSON metadata
 * - Cloud Storage Integration (Supabase, S3, Cloudinary, Local Download URL)
 */

const express = require('express');
const axios = require('axios');

const router = express.Router();
const PYTHON_PDF_SERVICE_URL = process.env.PDF_SERVICE_URL || 'http://127.0.0.1:5000';

// -------------------------------------------------------------------------
// 1. LIST ALL TEMPLATES
// GET /api/express/templates
// -------------------------------------------------------------------------
router.get('/templates', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_PDF_SERVICE_URL}/api/templates`);
        return res.json(response.data);
    } catch (error) {
        console.error("Error fetching templates:", error.message);
        return res.status(500).json({ error: "Failed to list templates", details: error.message });
    }
});

// -------------------------------------------------------------------------
// 2. GET SPECIFIC TEMPLATE & DETECTED VARIABLES
// GET /api/express/templates/:filename
// -------------------------------------------------------------------------
router.get('/templates/:filename', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_PDF_SERVICE_URL}/api/templates/${req.params.filename}`);
        return res.json(response.data);
    } catch (error) {
        console.error("Error fetching template details:", error.message);
        return res.status(500).json({ error: "Failed to fetch template", details: error.message });
    }
});

// -------------------------------------------------------------------------
// 3. ADD OR MODIFY CUSTOM HTML TEMPLATE
// POST /api/express/templates
// Body: { name: "Internship_Letter", html: "<html>...</html>" }
// -------------------------------------------------------------------------
router.post('/templates', async (req, res) => {
    try {
        const { name, html } = req.body;
        if (!name || !html) {
            return res.status(400).json({ error: "Both 'name' and 'html' string content are required" });
        }

        const response = await axios.post(`${PYTHON_PDF_SERVICE_URL}/api/templates`, { name, html });
        return res.status(201).json(response.data);
    } catch (error) {
        console.error("Error saving template:", error.message);
        return res.status(400).json({ error: "Failed to save custom template", details: error.response?.data || error.message });
    }
});

// -------------------------------------------------------------------------
// 4. DELETE CUSTOM TEMPLATE
// DELETE /api/express/templates/:filename
// -------------------------------------------------------------------------
router.delete('/templates/:filename', async (req, res) => {
    try {
        const response = await axios.delete(`${PYTHON_PDF_SERVICE_URL}/api/templates/${req.params.filename}`);
        return res.json(response.data);
    } catch (error) {
        console.error("Error deleting template:", error.message);
        return res.status(500).json({ error: "Failed to delete template", details: error.response?.data || error.message });
    }
});

// -------------------------------------------------------------------------
// 5. GENERATE SINGLE PDF & RETURN STRUCTURED METADATA + CLOUD URLS
// POST /api/express/generate-certificate-info
// Body: { template: "certificate.html", data: { name: "Sayaji Kapse", role: "AI Engineer", serial_no: "CPA-001" } }
// Returns: JSON with request_id, certificate_serial, local_download_url, Supabase / S3 / Cloudinary URLs
// -------------------------------------------------------------------------
router.post('/generate-certificate-info', async (req, res) => {
    try {
        const { template, data } = req.body;
        if (!template || !data) {
            return res.status(400).json({ error: "Both 'template' and 'data' are required" });
        }

        const response = await axios.post(`${PYTHON_PDF_SERVICE_URL}/api/generate-certificate-info`, { template, data });
        return res.json(response.data);

    } catch (error) {
        console.error("Error in structured certificate generation:", error.message);
        return res.status(500).json({ error: "Certificate info generation failed", details: error.response?.data || error.message });
    }
});

// -------------------------------------------------------------------------
// 6. BULK/BATCH GENERATION & RETURN STRUCTURED METADATA LIST + CLOUD URLS
// POST /api/express/generate-batch-info
// Body: { template: "certificate.html", data_list: [ { name: "Alice", ... }, { name: "Bob", ... } ] }
// -------------------------------------------------------------------------
router.post('/generate-batch-info', async (req, res) => {
    try {
        const { template, data_list } = req.body;
        if (!template || !data_list || !Array.isArray(data_list)) {
            return res.status(400).json({ error: "'template' name and 'data_list' array are required" });
        }

        const response = await axios.post(`${PYTHON_PDF_SERVICE_URL}/api/generate-batch-info`, { template, data_list });
        return res.json(response.data);

    } catch (error) {
        console.error("Error in structured batch generation:", error.message);
        return res.status(500).json({ error: "Batch certificate info generation failed", details: error.response?.data || error.message });
    }
});

// -------------------------------------------------------------------------
// 7. GENERATE SINGLE PDF & RETURN DIRECT BINARY FILE STREAM
// POST /api/express/generate-pdf
// -------------------------------------------------------------------------
router.post('/generate-pdf', async (req, res) => {
    try {
        const { template, data } = req.body;
        if (!template || !data) {
            return res.status(400).json({ error: "Both 'template' filename and 'data' object are required" });
        }

        const pdfResponse = await axios.post(`${PYTHON_PDF_SERVICE_URL}/api/generate-pdf`, { template, data }, {
            responseType: 'arraybuffer'
        });

        const safeName = (data.name || 'document').replace(/ /g, '_');
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', `attachment; filename="${template.replace('.html','')}_${safeName}.pdf"`);
        return res.send(Buffer.from(pdfResponse.data));

    } catch (error) {
        console.error("Error generating single PDF:", error.message);
        return res.status(500).json({ error: "PDF generation failed", details: error.message });
    }
});

// -------------------------------------------------------------------------
// 8. BULK GENERATION & RETURN DIRECT ZIP ARCHIVE STREAM
// POST /api/express/generate-batch
// -------------------------------------------------------------------------
router.post('/generate-batch', async (req, res) => {
    try {
        const { template, data_list } = req.body;
        if (!template || !data_list || !Array.isArray(data_list)) {
            return res.status(400).json({ error: "'template' name and 'data_list' array are required" });
        }

        const zipResponse = await axios.post(`${PYTHON_PDF_SERVICE_URL}/api/generate-batch-pdf`, { template, data_list }, {
            responseType: 'arraybuffer'
        });

        res.setHeader('Content-Type', 'application/zip');
        res.setHeader('Content-Disposition', `attachment; filename="Bulk_Certificates_${Date.now()}.zip"`);
        return res.send(Buffer.from(zipResponse.data));

    } catch (error) {
        console.error("Error generating bulk PDFs:", error.message);
        return res.status(500).json({ error: "Batch PDF generation failed", details: error.message });
    }
});

module.exports = router;
