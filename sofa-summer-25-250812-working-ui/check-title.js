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
  
  const titleInfo = await page.evaluate(() => {
    const dashboard = document.querySelector('.dashboard-container');
    const headerDiv = dashboard?.querySelector('.sofa-header');
    const logoContainer = headerDiv?.querySelector('.sofa-logo-title');
    const subtitle = headerDiv?.querySelector('.sofa-subtitle');
    
    const dashboardRect = dashboard?.getBoundingClientRect();
    const headerRect = headerDiv?.getBoundingClientRect();
    const logoRect = logoContainer?.getBoundingClientRect();
    const subtitleRect = subtitle?.getBoundingClientRect();
    
    const dashboardStyles = dashboard ? window.getComputedStyle(dashboard) : null;
    const headerStyles = headerDiv ? window.getComputedStyle(headerDiv) : null;
    const logoStyles = logoContainer ? window.getComputedStyle(logoContainer) : null;
    const subtitleStyles = subtitle ? window.getComputedStyle(subtitle) : null;
    
    return {
      dashboard: {
        width: dashboardRect?.width,
        left: dashboardRect?.left,
        textAlign: dashboardStyles?.textAlign
      },
      header: {
        width: headerRect?.width,
        left: headerRect?.left,
        textAlign: headerStyles?.textAlign
      },
      logoContainer: {
        width: logoRect?.width,
        left: logoRect?.left,
        right: logoRect?.right,
        display: logoStyles?.display,
        justifyContent: logoStyles?.justifyContent,
        centerOffset: logoRect ? (dashboardRect.left + dashboardRect.width/2) - (logoRect.left + logoRect.width/2) : null
      },
      subtitle: {
        width: subtitleRect?.width,
        left: subtitleRect?.left,
        right: subtitleRect?.right,
        maxWidth: subtitleStyles?.maxWidth,
        margin: subtitleStyles?.margin,
        centerOffset: subtitleRect ? (dashboardRect.left + dashboardRect.width/2) - (subtitleRect.left + subtitleRect.width/2) : null
      }
    };
  });
  
  console.log(JSON.stringify(titleInfo, null, 2));
  
  await browser.close();
})();