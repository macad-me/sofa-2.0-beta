const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  // Test different viewport sizes
  const viewports = [
    { width: 768, height: 1024, name: 'tablet' },
    { width: 1024, height: 768, name: 'small-desktop' },
    { width: 1440, height: 900, name: 'desktop' },
  ];
  
  console.log('=== ANALYZING STYLE CONFLICTS ===\n');
  
  for (const viewport of viewports) {
    await page.setViewport(viewport);
    await page.goto('http://localhost:5173/sofa-web-ui-preview/macos/sequoia', { 
      waitUntil: 'networkidle0'
    });
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const analysis = await page.evaluate(() => {
      // Find elements with data-v-* attributes
      const elements = document.querySelectorAll('[data-v-a6882923], [data-v-014f9d3d]');
      const results = [];
      
      elements.forEach(el => {
        const attrs = Array.from(el.attributes)
          .filter(attr => attr.name.startsWith('data-v-'))
          .map(attr => attr.name);
        
        const styles = window.getComputedStyle(el);
        results.push({
          tag: el.tagName,
          class: el.className,
          dataAttrs: attrs,
          display: styles.display,
          visibility: styles.visibility,
          position: styles.position,
          width: styles.width,
          zIndex: styles.zIndex,
          isVisible: el.offsetParent !== null
        });
      });
      
      // Check VPDocAside specifically
      const aside = document.querySelector('.VPDocAside');
      const outline = document.querySelector('.VPDocOutline');
      const title = document.querySelector('h1');
      
      return {
        scopedElements: results,
        aside: aside ? {
          found: true,
          display: window.getComputedStyle(aside).display,
          position: window.getComputedStyle(aside).position,
          width: window.getComputedStyle(aside).width,
          right: window.getComputedStyle(aside).right,
          isVisible: aside.offsetParent !== null
        } : { found: false },
        outline: outline ? {
          found: true,
          display: window.getComputedStyle(outline).display,
          isVisible: outline.offsetParent !== null
        } : { found: false },
        title: title ? {
          found: true,
          rect: title.getBoundingClientRect(),
          isObscured: false // Will check if aside overlaps
        } : { found: false }
      };
    });
    
    console.log(`\n=== ${viewport.name.toUpperCase()} (${viewport.width}x${viewport.height}) ===`);
    console.log('Scoped elements found:', analysis.scopedElements.length);
    if (analysis.scopedElements.length > 0) {
      console.log('Data attributes:', analysis.scopedElements.map(el => el.dataAttrs).flat());
    }
    console.log('Aside:', analysis.aside);
    console.log('Outline:', analysis.outline);
    if (analysis.title.found) {
      console.log('Title position:', analysis.title.rect);
    }
  }
  
  await browser.close();
})();