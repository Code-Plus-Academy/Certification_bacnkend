/**
 * Express.js Integration Examples for PDF & Certificate Automation
 * 
 * Shows 3 different ways to integrate Express.js with the PDF Automation Engine.
 */

const express = require('express');
const axios = require('axios'); // or native fetch
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(express.json());

// =========================================================================
// APPROACH 1: HTTP REST API Microservice (RECOMMENDED FOR PRODUCTION)
// The Python app runs as a service on http://localhost:5000 (or Docker/Cloud Run)
// =========================================================================
app.post('/api/express/generate-certificate', async (req, res) => {
    try {
        const payload = {
            template: req.body.template || 'certificate.html',
            data: {
                name: req.body.name || 'Sayaji Kapse',
                role: req.body.role || 'Full Stack Web & AI Developer',
                serial_no: req.body.serial_no || 'CPA-2026-SK-9988',
                organization_name: 'Code Plus Academy',
                date: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
            }
        };

        // Call the Python PDF Microservice API
        const pdfResponse = await axios.post('http://127.0.0.1:5000/api/generate-pdf', payload, {
            responseType: 'arraybuffer' // Receive binary PDF buffer
        });

        // Set response headers and return PDF binary stream directly to client
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', `attachment; filename="${payload.data.name.replace(/ /g, '_')}_Certificate.pdf"`);
        return res.send(Buffer.from(pdfResponse.data));

    } catch (error) {
        console.error("PDF Generation Error:", error.message);
        return res.status(500).json({ error: "Failed to generate PDF", details: error.message });
    }
});


// =========================================================================
// APPROACH 2: DIRECT CLI CHILD PROCESS EXECUTION
// If Express and Python run on the same server, call `python cli.py`
// =========================================================================
app.post('/api/express/cli-generate', (req, res) => {
    const templateName = req.body.template || 'offer_letter.html';
    const candidateData = JSON.stringify(req.body.data || {
        name: 'Jane Doe',
        role: 'Senior Developer',
        duration: '24 Months',
        serial_no: 'KT-2026-001',
        date: 'August 06, 2026',
        company_name: 'Kalki Technology Pvt. Ltd.',
        holding_company: 'Neeta Holdings Pvt. Ltd.'
    });

    const outputPdfName = `Offer_Letter_${Date.now()}.pdf`;
    const pythonScriptPath = path.join(__dirname, 'cli.py');

    // Execute Python CLI process from Node.js
    execFile('python', [pythonScriptPath, '--template', templateName, '--json', candidateData, '--output', outputPdfName], (error, stdout, stderr) => {
        if (error) {
            console.error("CLI Execution Error:", stderr);
            return res.status(500).json({ error: "CLI PDF generation failed", stderr });
        }

        const generatedPdfPath = path.join(__dirname, 'output', outputPdfName);
        return res.download(generatedPdfPath);
    });
});


// =========================================================================
// APPROACH 3: PURE NODE.JS NATIVE (Handlebars + Puppeteer)
// If you want a 100% JavaScript backend without Python
// =========================================================================
/*
npm install handlebars puppeteer

const handlebars = require('handlebars');
const puppeteer = require('puppeteer');

app.post('/api/express/native-pdf', async (req, res) => {
    const htmlTemplate = fs.readFileSync(path.join(__dirname, 'templates/certificate.html'), 'utf8');
    const template = handlebars.compile(htmlTemplate);
    const renderedHtml = template(req.body.data);

    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    await page.setContent(renderedHtml, { waitUntil: 'networkidle0' });
    const pdfBuffer = await page.pdf({ format: 'A4', landscape: true, printBackground: true });
    await browser.close();

    res.setHeader('Content-Type', 'application/pdf');
    return res.send(pdfBuffer);
});
*/

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Express Backend Server listening on http://localhost:${PORT}`);
});
