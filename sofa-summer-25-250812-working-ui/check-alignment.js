const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  
  await page.goto('http://localhost:5173/sofa-web-ui-preview/', { 
    waitUntil: 'networkidle0'
  });
  
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  const alignmentInfo = await page.evaluate(() => {
    const firstCard = document.querySelector('.bento-card');
    const header = firstCard?.querySelector('.bento-card-header');
    const icon = header?.querySelector('.bento-card-icon');
    const title = header?.querySelector('.bento-card-title');
    
    const headerRect = header?.getBoundingClientRect();
    const iconRect = icon?.getBoundingClientRect();
    const titleRect = title?.getBoundingClientRect();
    
    const headerStyles = header ? window.getComputedStyle(header) : null;
    const iconStyles = icon ? window.getComputedStyle(icon) : null;
    const titleStyles = title ? window.getComputedStyle(title) : null;
    
    return {
      header: {
        display: headerStyles?.display,
        alignItems: headerStyles?.alignItems,
        gap: headerStyles?.gap,
        height: headerRect?.height
      },
      icon: {
        width: iconStyles?.width,
        height: iconStyles?.height,
        display: iconStyles?.display,
        alignItems: iconStyles?.alignItems,
        justifyContent: iconStyles?.justifyContent,
        top: iconRect?.top,
        centerY: iconRect ? iconRect.top + iconRect.height/2 : null
      },
      title: {
        fontSize: titleStyles?.fontSize,
        lineHeight: titleStyles?.lineHeight,
        top: titleRect?.top,
        height: titleRect?.height,
        centerY: titleRect ? titleRect.top + titleRect.height/2 : null
      },
      alignment: {
        verticalOffset: (iconRect && titleRect) ? 
          (iconRect.top + iconRect.height/2) - (titleRect.top + titleRect.height/2) : null
      }
    };
  });
  
  console.log(JSON.stringify(alignmentInfo, null, 2));
  await browser.close();
})();