const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  
  await page.goto('http://localhost:5173/sofa-web-ui-preview/', { 
    waitUntil: 'networkidle0',
    timeout: 10000 
  });
  
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  const hierarchy = await page.evaluate(() => {
    const dashboard = document.querySelector('.dashboard-container');
    if (!dashboard) return { error: 'Dashboard not found' };
    
    let element = dashboard;
    const path = [];
    
    while (element && element !== document.body) {
      const styles = window.getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      path.push({
        tag: element.tagName,
        class: element.className || '(no class)',
        id: element.id || '(no id)',
        margin: styles.margin,
        padding: styles.padding,
        width: rect.width + 'px',
        computedWidth: styles.width,
        maxWidth: styles.maxWidth,
        display: styles.display,
        position: styles.position
      });
      element = element.parentElement;
    }
    
    return path.reverse();
  });
  
  console.log('Element hierarchy from body to dashboard:');
  console.log(JSON.stringify(hierarchy, null, 2));
  
  await browser.close();
})();