/**
 * Capture the dashboard views as PNG files for the executive report.
 *
 * The Streamlit server must already be running on port 8501:
 *     streamlit run dashboard/app.py
 *
 * Run with:
 *     NODE_PATH=<path to playwright> [PW_CHANNEL=chrome] node src/capture_dashboard.js
 */

const path = require('path');
const { chromium } = require('playwright');

const BASE_URL = 'http://localhost:8501';
const OUTPUT_DIR = path.join(__dirname, '..', 'images');

const VIEWS = [
  { tab: 'Composición del catálogo', file: 'dashboard-01-composicion.png' },
  { tab: 'Desempeño de contenidos', file: 'dashboard-02-desempeno.png' },
  { tab: 'Dimensión financiera', file: 'dashboard-03-financiera.png' },
];

async function settle(page) {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3500);
}

/**
 * Streamlit renders inside its own scroll container, so `fullPage` cannot reach
 * the bottom of a view. The viewport is resized to the real content height
 * instead, which also removes the empty space left by a fixed tall viewport.
 */
async function fitViewportToContent(page) {
  const height = await page.evaluate(() => {
    const main = document.querySelector('section.main, [data-testid="stMain"]') || document.body;
    const container = main.querySelector('.block-container') || main;
    return Math.ceil(container.getBoundingClientRect().height) + 80;
  });
  const clamped = Math.min(Math.max(height, 900), 6000);
  await page.setViewportSize({ width: 1680, height: clamped });
  await page.waitForTimeout(2500);
}

(async () => {
  const browser = await chromium.launch(process.env.PW_CHANNEL ? { channel: process.env.PW_CHANNEL } : {});
  const page = await browser.newPage({
    viewport: { width: 1680, height: 2400 },
    deviceScaleFactor: 2,
  });

  await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('.sv-header', { timeout: 60000 });
  await settle(page);

  // Streamlit's floating toolbar and footer are runtime chrome, not part of the
  // dashboard design, so they are hidden before capturing.
  await page.addStyleTag({
    content: `
      [data-testid="stToolbar"], [data-testid="stDecoration"],
      [data-testid="stStatusWidget"], footer { display: none !important; }
    `,
  });

  for (const view of VIEWS) {
    await page.setViewportSize({ width: 1680, height: 1200 });
    await page.getByRole('tab', { name: view.tab }).click();
    await settle(page);
    await fitViewportToContent(page);

    const target = path.join(OUTPUT_DIR, view.file);
    await page.screenshot({ path: target, fullPage: true });
    console.log(`saved ${view.file}`);
  }

  // Detail capture: the data-quality control and its effect on the comparison.
  await page.setViewportSize({ width: 1680, height: 1200 });
  await page.getByRole('tab', { name: 'Desempeño de contenidos' }).click();
  await settle(page);
  await page
    .getByTestId('stSidebarUserContent')
    .getByText('Excluir títulos sin votos')
    .click();
  await settle(page);
  await fitViewportToContent(page);
  await page.screenshot({
    path: path.join(OUTPUT_DIR, 'dashboard-04-filtro-calidad.png'),
    fullPage: true,
  });
  console.log('saved dashboard-04-filtro-calidad.png');

  await browser.close();
})().catch((error) => {
  console.error('capture failed:', error.message);
  process.exit(1);
});
