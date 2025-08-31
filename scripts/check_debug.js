import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  console.log('=== Checking Debug Panel on Different Pages ===\n');
  
  // Check index page
  await page.goto('http://localhost:5173/sofa-2.0/', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 1000));
  
  // Click to expand the debug panel
  await page.evaluate(() => {
    const toggleBtn = document.querySelector('.data-source-debug .toggle-btn');
    if (toggleBtn) toggleBtn.click();
  });
  await new Promise(r => setTimeout(r, 500));
  
  const indexDebug = await page.evaluate(() => {
    const debugEl = document.querySelector('.data-source-debug');
    if (debugEl) {
      const sources = [];
      debugEl.querySelectorAll('.source-item').forEach(item => {
        const label = item.querySelector('.source-label')?.textContent;
        const path = item.querySelector('.source-path')?.textContent;
        if (label && path) sources.push(`${label} ${path}`);
      });
      return { found: true, sources, expanded: !!debugEl.querySelector('.debug-content') };
    }
    return { found: false };
  });
  
  console.log('Index page (/)');
  console.log('Debug panel found:', indexDebug.found);
  if (indexDebug.sources) {
    console.log('Data sources:', indexDebug.sources);
  }
  
  // Check macOS Sequoia page
  console.log('\n---');
  await page.goto('http://localhost:5173/sofa-2.0/macos/sequoia', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 1000));
  
  const macosDebug = await page.evaluate(() => {
    const debugEl = document.querySelector('.data-source-debug');
    if (debugEl) {
      const sources = [];
      debugEl.querySelectorAll('.source-item').forEach(item => {
        const label = item.querySelector('.source-label')?.textContent;
        const path = item.querySelector('.source-path')?.textContent;
        if (label && path) sources.push(`${label} ${path}`);
      });
      return { found: true, sources };
    }
    return { found: false };
  });
  
  console.log('macOS Sequoia page (/macos/sequoia)');
  console.log('Debug panel found:', macosDebug.found);
  if (macosDebug.sources) {
    console.log('Data sources:', macosDebug.sources);
  }
  
  // Check iOS page
  console.log('\n---');
  await page.goto('http://localhost:5173/sofa-2.0/ios/ios18', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 1000));
  
  const iosDebug = await page.evaluate(() => {
    const debugEl = document.querySelector('.data-source-debug');
    if (debugEl) {
      const sources = [];
      debugEl.querySelectorAll('.source-item').forEach(item => {
        const label = item.querySelector('.source-label')?.textContent;
        const path = item.querySelector('.source-path')?.textContent;
        if (label && path) sources.push(`${label} ${path}`);
      });
      return { found: true, sources };
    }
    return { found: false };
  });
  
  console.log('iOS 18 page (/ios/ios18)');
  console.log('Debug panel found:', iosDebug.found);
  if (iosDebug.sources) {
    console.log('Data sources:', iosDebug.sources);
  }
  
  await browser.close();
})();