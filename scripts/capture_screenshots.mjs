import fs from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(new URL("../../Data-Center-AI-BI-Operations-Console/package.json", import.meta.url));
const { chromium } = require("playwright");

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const imageDir = path.join(root, "docs", "images");
await fs.mkdir(imageDir, { recursive: true });

const mime = {
  ".html": "text/html",
  ".js": "text/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".csv": "text/csv",
  ".png": "image/png",
};

const server = http.createServer(async (req, res) => {
  const rawPath = decodeURIComponent(new URL(req.url, "http://localhost").pathname);
  const filePath = path.join(root, rawPath === "/" ? "index.html" : rawPath);
  if (!filePath.startsWith(root)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }
  try {
    const data = await fs.readFile(filePath);
    res.writeHead(200, { "Content-Type": mime[path.extname(filePath)] || "application/octet-stream" });
    res.end(data);
  } catch {
    res.writeHead(404);
    res.end("Not found");
  }
});

await new Promise((resolve) => server.listen(4297, "127.0.0.1", resolve));

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });
await page.goto("http://127.0.0.1:4297", { waitUntil: "networkidle" });

await page.locator("#cockpit").screenshot({ path: path.join(imageDir, "cockpit.png") });
await page.locator("#queue").screenshot({ path: path.join(imageDir, "queue.png") });
await page.locator("#requirements").screenshot({ path: path.join(imageDir, "requirements.png") });
await page.locator("#scenarios").screenshot({ path: path.join(imageDir, "scenarios.png") });
await fs.copyFile(path.join(imageDir, "cockpit.png"), path.join(imageDir, "dashboard.png"));

const checks = await page.evaluate(() => ({
  title: document.title,
  metrics: document.querySelectorAll(".metric-card").length,
  siteRows: document.querySelectorAll("#site-table tr").length,
  initiativeCards: document.querySelectorAll(".initiative-card").length,
  requirementCards: document.querySelectorAll(".requirement-card").length,
  scenarioCards: document.querySelectorAll(".scenario-card").length,
}));

await browser.close();
server.close();

console.log(JSON.stringify(checks, null, 2));
