/**
 * Render the report figures from HTML to PNG.
 *
 * Run with:
 *     NODE_PATH=<path to playwright> [PW_CHANNEL=chrome] node src/render_figures.js
 */

const path = require('path');
const { chromium } = require('playwright');

const FIGURES = [
  { html: 'arquitectura.html', png: 'figura-arquitectura.png' },
  { html: 'recomendaciones.html', png: 'figura-recomendaciones.png' },
];

(async () => {
  const browser = await chromium.launch(process.env.PW_CHANNEL ? { channel: process.env.PW_CHANNEL } : {});
  const page = await browser.newPage({ deviceScaleFactor: 2 });

  for (const figure of FIGURES) {
    const source = path.join(__dirname, 'figures', figure.html);
    await page.goto(`file://${source}`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);

    const target = path.join(__dirname, '..', 'images', figure.png);
    await page.locator('body').screenshot({ path: target });
    console.log(`saved ${figure.png}`);
  }

  await browser.close();
})().catch((error) => {
  console.error('render failed:', error.message);
  process.exit(1);
});
