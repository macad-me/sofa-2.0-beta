const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  
  // Navigate to a page with sidebar (not home)
  await page.goto('http://localhost:5173/sofa-web-ui-preview/macos/sequoia', { 
    waitUntil: 'networkidle0'
  });
  
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  const layoutInfo = await page.evaluate(() => {
    const sidebar = document.querySelector('.VPSidebar');
    const content = document.querySelector('.VPContent');
    const mainDoc = document.querySelector('.VPDoc');
    const onThisPage = document.querySelector('.VPDocOutlineTitle');
    const container = document.querySelector('.container');
    
    const sidebarRect = sidebar?.getBoundingClientRect();
    const contentRect = content?.getBoundingClientRect();
    const mainDocRect = mainDoc?.getBoundingClientRect();
    const onThisPageRect = onThisPage?.getBoundingClientRect();
    
    const sidebarStyles = sidebar ? window.getComputedStyle(sidebar) : null;
    const contentStyles = content ? window.getComputedStyle(content) : null;
    const mainDocStyles = mainDoc ? window.getComputedStyle(mainDoc) : null;
    
    return {
      viewport: {
        width: window.innerWidth
      },
      sidebar: {
        found: !!sidebar,
        width: sidebarRect?.width,
        computedWidth: sidebarStyles?.width,
        left: sidebarRect?.left,
        position: sidebarStyles?.position
      },
      content: {
        found: !!content,
        width: contentRect?.width,
        left: contentRect?.left,
        marginLeft: contentStyles?.marginLeft,
        paddingLeft: contentStyles?.paddingLeft,
        maxWidth: contentStyles?.maxWidth
      },
      mainDoc: {
        found: !!mainDoc,
        width: mainDocRect?.width,
        padding: mainDocStyles?.padding,
        maxWidth: mainDocStyles?.maxWidth
      },
      onThisPage: {
        found: !!onThisPage,
        left: onThisPageRect?.left,
        text: onThisPage?.textContent
      },
      usableContentWidth: contentRect ? contentRect.width - parseInt(contentStyles.paddingLeft) - parseInt(contentStyles.paddingRight) : null
    };
  });
  
  console.log(JSON.stringify(layoutInfo, null, 2));
  await browser.close();
})();