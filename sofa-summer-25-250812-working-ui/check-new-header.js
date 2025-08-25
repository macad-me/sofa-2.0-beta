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
  
  const headerInfo = await page.evaluate(() => {
    const dashboard = document.querySelector('.dashboard-container');
    const header = dashboard?.querySelector('.sofa-header');
    const imageContainer = header?.querySelector('.sofa-image-container');
    const name = header?.querySelector('.sofa-name');
    const tagline = header?.querySelector('.sofa-tagline');
    
    const dashboardRect = dashboard?.getBoundingClientRect();
    const headerRect = header?.getBoundingClientRect();
    const imageRect = imageContainer?.getBoundingClientRect();
    const nameRect = name?.getBoundingClientRect();
    const taglineRect = tagline?.getBoundingClientRect();
    
    const dashboardCenter = dashboardRect ? dashboardRect.left + dashboardRect.width/2 : null;
    
    return {
      dashboard: {
        width: dashboardRect?.width,
        left: dashboardRect?.left,
        center: dashboardCenter
      },
      header: {
        width: headerRect?.width,
        display: header ? window.getComputedStyle(header).display : null,
        alignItems: header ? window.getComputedStyle(header).alignItems : null,
        textAlign: header ? window.getComputedStyle(header).textAlign : null
      },
      imageContainer: {
        width: imageRect?.width,
        left: imageRect?.left,
        center: imageRect ? imageRect.left + imageRect.width/2 : null,
        offsetFromDashboardCenter: imageRect && dashboardCenter ? 
          (imageRect.left + imageRect.width/2) - dashboardCenter : null
      },
      name: {
        width: nameRect?.width,
        left: nameRect?.left,
        center: nameRect ? nameRect.left + nameRect.width/2 : null,
        offsetFromDashboardCenter: nameRect && dashboardCenter ? 
          (nameRect.left + nameRect.width/2) - dashboardCenter : null
      },
      tagline: {
        width: taglineRect?.width,
        left: taglineRect?.left,
        center: taglineRect ? taglineRect.left + taglineRect.width/2 : null,
        offsetFromDashboardCenter: taglineRect && dashboardCenter ? 
          (taglineRect.left + taglineRect.width/2) - dashboardCenter : null
      }
    };
  });
  
  console.log(JSON.stringify(headerInfo, null, 2));
  
  await browser.close();
})();