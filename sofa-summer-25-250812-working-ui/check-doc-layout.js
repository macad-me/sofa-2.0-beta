const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  
  await page.goto('http://localhost:5173/sofa-web-ui-preview/macos/sequoia', { 
    waitUntil: 'networkidle0'
  });
  
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  const layoutInfo = await page.evaluate(() => {
    // Get all key elements
    const sidebar = document.querySelector('.VPSidebar');
    const content = document.querySelector('.VPContent');
    const doc = document.querySelector('.VPDoc');
    const docContainer = doc?.querySelector('.container');
    const docContent = doc?.querySelector('.content');
    const aside = document.querySelector('.VPDocAside');
    const outline = document.querySelector('.VPDocOutline');
    const onThisPageTitle = document.querySelector('.outline-title');
    
    // Get all measurements
    const getRect = (el) => el ? el.getBoundingClientRect() : null;
    const getStyles = (el) => el ? window.getComputedStyle(el) : null;
    
    const sidebarRect = getRect(sidebar);
    const contentRect = getRect(content);
    const docRect = getRect(doc);
    const docContainerRect = getRect(docContainer);
    const asideRect = getRect(aside);
    
    const contentStyles = getStyles(content);
    const docStyles = getStyles(doc);
    const docContainerStyles = getStyles(docContainer);
    
    // Calculate actual content area
    const viewportWidth = window.innerWidth;
    const sidebarWidth = sidebarRect?.width || 0;
    const availableWidth = viewportWidth - sidebarWidth;
    
    return {
      viewport: {
        width: viewportWidth
      },
      sidebar: {
        found: !!sidebar,
        width: sidebarRect?.width,
        left: sidebarRect?.left
      },
      content: {
        found: !!content,
        width: contentRect?.width,
        left: contentRect?.left,
        marginLeft: contentStyles?.marginLeft,
        paddingLeft: contentStyles?.paddingLeft,
        paddingRight: contentStyles?.paddingRight
      },
      doc: {
        found: !!doc,
        width: docRect?.width,
        left: docRect?.left,
        padding: docStyles?.padding,
        maxWidth: docStyles?.maxWidth,
        margin: docStyles?.margin
      },
      docContainer: {
        found: !!docContainer,
        width: docContainerRect?.width,
        left: docContainerRect?.left,
        padding: docContainerStyles?.padding,
        margin: docContainerStyles?.margin
      },
      aside: {
        found: !!aside,
        width: asideRect?.width,
        left: asideRect?.left,
        hasOutline: !!outline,
        onThisPageTitle: onThisPageTitle?.textContent
      },
      layout: {
        availableWidth: availableWidth,
        totalContentWidth: docRect?.width,
        centerOffset: docRect ? (docRect.left - sidebarWidth) - ((availableWidth - docRect.width) / 2) : null
      }
    };
  });
  
  console.log(JSON.stringify(layoutInfo, null, 2));
  await browser.close();
})();