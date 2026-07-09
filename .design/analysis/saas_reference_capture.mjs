import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const outputDir = path.join(root, '.design', 'reference', 'saas-study');
const pages = [
  {
    product: 'linear',
    name: 'home',
    url: 'https://linear.app',
  },
  {
    product: 'linear',
    name: 'issue-tracking',
    url: 'https://linear.app/features/issue-tracking',
  },
  {
    product: 'elevenlabs',
    name: 'home',
    url: 'https://elevenlabs.io',
  },
  {
    product: 'elevenlabs',
    name: 'conversational-ai',
    url: 'https://elevenlabs.io/conversational-ai',
  },
  {
    product: 'vercel',
    name: 'home',
    url: 'https://vercel.com',
  },
  {
    product: 'vercel',
    name: 'analytics-docs',
    url: 'https://vercel.com/docs/analytics',
  },
  {
    product: 'vercel',
    name: 'observability',
    url: 'https://vercel.com/features/observability',
  },
];

const viewports = [
  { name: 'desktop', width: 1440, height: 1100 },
  { name: 'mobile', width: 390, height: 844 },
];

function slug(value) {
  return value.replace(/[^a-z0-9-]+/gi, '-').replace(/^-|-$/g, '').toLowerCase();
}

async function dismissOverlays(page) {
  const candidates = [
    'button:has-text("Accept")',
    'button:has-text("Accept all")',
    'button:has-text("Allow all")',
    'button:has-text("Got it")',
    'button:has-text("Continue")',
    'button[aria-label*="close" i]',
    'button[aria-label*="dismiss" i]',
  ];

  for (const selector of candidates) {
    try {
      const locator = page.locator(selector).first();
      if (await locator.isVisible({ timeout: 1200 })) {
        await locator.click({ timeout: 1200 });
        await page.waitForTimeout(500);
      }
    } catch {
      // Ignore sites that do not show the overlay.
    }
  }
}

async function extractPageData(page) {
  return page.evaluate(() => {
    const text = (node) => (node?.innerText || node?.textContent || '').trim().replace(/\s+/g, ' ');
    const css = (node) => getComputedStyle(node);
    const visible = (node) => {
      const rect = node.getBoundingClientRect();
      const style = css(node);
      return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
    };
    const sample = (selector, limit = 30) => Array.from(document.querySelectorAll(selector))
      .filter(visible)
      .slice(0, limit)
      .map((node) => {
        const rect = node.getBoundingClientRect();
        const style = css(node);
        return {
          tag: node.tagName.toLowerCase(),
          text: text(node).slice(0, 180),
          className: String(node.className || '').slice(0, 160),
          role: node.getAttribute('role'),
          ariaLabel: node.getAttribute('aria-label'),
          href: node.getAttribute('href'),
          rect: {
            x: Math.round(rect.x),
            y: Math.round(rect.y),
            w: Math.round(rect.width),
            h: Math.round(rect.height),
          },
          style: {
            fontFamily: style.fontFamily,
            fontSize: style.fontSize,
            fontWeight: style.fontWeight,
            lineHeight: style.lineHeight,
            color: style.color,
            backgroundColor: style.backgroundColor,
            borderColor: style.borderColor,
            borderRadius: style.borderRadius,
            boxShadow: style.boxShadow,
            display: style.display,
            gap: style.gap,
            padding: style.padding,
            transition: style.transition,
          },
        };
      });

    const colorSet = new Set();
    const spacingSet = new Set();
    const radiusSet = new Set();
    const shadowSet = new Set();
    const transitionSet = new Set();

    Array.from(document.querySelectorAll('body *')).filter(visible).slice(0, 700).forEach((node) => {
      const style = css(node);
      [
        style.color,
        style.backgroundColor,
        style.borderColor,
      ].filter((value) => value && value !== 'rgba(0, 0, 0, 0)' && value !== 'transparent').forEach((value) => colorSet.add(value));
      [
        style.marginTop,
        style.marginBottom,
        style.marginLeft,
        style.marginRight,
        style.paddingTop,
        style.paddingBottom,
        style.paddingLeft,
        style.paddingRight,
        style.gap,
        style.rowGap,
        style.columnGap,
      ].filter((value) => value && value !== '0px' && value !== 'normal').forEach((value) => spacingSet.add(value));
      if (style.borderRadius && style.borderRadius !== '0px') radiusSet.add(style.borderRadius);
      if (style.boxShadow && style.boxShadow !== 'none') shadowSet.add(style.boxShadow);
      if (style.transition && style.transition !== 'all') transitionSet.add(style.transition);
    });

    const sections = Array.from(document.querySelectorAll('header, nav, main, section, aside, footer, [role="navigation"], [role="main"]'))
      .filter(visible)
      .slice(0, 40)
      .map((node) => {
        const rect = node.getBoundingClientRect();
        const style = css(node);
        return {
          tag: node.tagName.toLowerCase(),
          role: node.getAttribute('role'),
          className: String(node.className || '').slice(0, 160),
          heading: text(node.querySelector('h1,h2,h3')).slice(0, 160),
          text: text(node).slice(0, 260),
          rect: {
            x: Math.round(rect.x),
            y: Math.round(rect.y),
            w: Math.round(rect.width),
            h: Math.round(rect.height),
          },
          style: {
            backgroundColor: style.backgroundColor,
            color: style.color,
            display: style.display,
            gridTemplateColumns: style.gridTemplateColumns,
            gap: style.gap,
            padding: style.padding,
          },
        };
      });

    return {
      title: document.title,
      url: location.href,
      bodyBackground: css(document.body).backgroundColor,
      headings: sample('h1,h2,h3,h4', 40),
      navLinks: sample('header a, nav a, [role="navigation"] a', 45),
      buttons: sample('button, a[role="button"], input[type="button"], input[type="submit"]', 30),
      inputs: sample('input, textarea, select', 20),
      cards: sample('article, [class*="card" i], [class*="panel" i], [class*="tile" i]', 45),
      badges: sample('[class*="badge" i], [class*="pill" i], [class*="tag" i], [class*="status" i]', 40),
      media: sample('img, video, canvas, svg', 35),
      tables: sample('table, [role="table"], [class*="table" i]', 15),
      sections,
      tokens: {
        colors: Array.from(colorSet).slice(0, 80),
        spacing: Array.from(spacingSet).slice(0, 70),
        radii: Array.from(radiusSet).slice(0, 40),
        shadows: Array.from(shadowSet).slice(0, 30),
        transitions: Array.from(transitionSet).slice(0, 40),
      },
    };
  });
}

async function captureSectionShots(page, product, name, viewportName) {
  const handles = await page.$$('header, nav, main > section, section, footer');
  const sectionFiles = [];
  let index = 0;

  for (const handle of handles.slice(0, 8)) {
    const box = await handle.boundingBox();
    if (!box || box.width < 160 || box.height < 80) continue;
    const file = `${product}-${name}-${viewportName}-section-${String(index + 1).padStart(2, '0')}.png`;
    try {
      await handle.screenshot({ path: path.join(outputDir, file) });
      sectionFiles.push(file);
      index += 1;
    } catch {
      // Some animated/cross-origin sections cannot be screenshotted reliably.
    }
  }
  return sectionFiles;
}

await fs.mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const results = [];

for (const target of pages) {
  for (const viewport of viewports) {
    const page = await browser.newPage({
      viewport: { width: viewport.width, height: viewport.height },
      deviceScaleFactor: 1,
      colorScheme: 'dark',
    });
    page.setDefaultTimeout(18000);

    const prefix = `${target.product}-${slug(target.name)}-${viewport.name}`;
    const fullPageFile = `${prefix}-full.png`;
    let error = null;
    let data = null;
    let sectionFiles = [];

    try {
      await page.goto(target.url, { waitUntil: 'domcontentloaded', timeout: 45000 });
      await page.waitForLoadState('networkidle', { timeout: 18000 }).catch(() => {});
      await dismissOverlays(page);
      await page.waitForTimeout(1800);
      await page.screenshot({ path: path.join(outputDir, fullPageFile), fullPage: true });
      sectionFiles = await captureSectionShots(page, target.product, slug(target.name), viewport.name);
      data = await extractPageData(page);
    } catch (captureError) {
      error = captureError.message;
    }

    results.push({
      ...target,
      viewport,
      fullPageFile,
      sectionFiles,
      error,
      data,
    });

    await page.close();
  }
}

await browser.close();
await fs.writeFile(path.join(outputDir, 'capture-summary.json'), JSON.stringify({ capturedAt: new Date().toISOString(), results }, null, 2));
console.log(`Saved ${results.length} captures to ${outputDir}`);
