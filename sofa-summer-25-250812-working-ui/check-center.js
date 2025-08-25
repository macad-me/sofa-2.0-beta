const puppeteer = require('puppeteer');

(async () => {
  try {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900 });
    
    await page.goto('http://localhost:5173/sofa-web-ui-preview/', { 
      waitUntil: 'networkidle0',
      timeout: 10000 
    });
    
    // Wait a bit for any dynamic content
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const info = await page.evaluate(() => {
      const dashboard = document.querySelector('.dashboard-container');
      const mainContent = document.querySelector('.main-content');
      const body = document.body;
      
      if (!dashboard) {
        return { error: 'Dashboard container not found' };
      }
      
      const dashboardRect = dashboard.getBoundingClientRect();
      const dashboardStyles = window.getComputedStyle(dashboard);
      const mainStyles = mainContent ? window.getComputedStyle(mainContent) : null;
      const bodyWidth = body.getBoundingClientRect().width;
      
      // Calculate if centered
      const leftSpace = dashboardRect.left;
      const rightSpace = bodyWidth - dashboardRect.right;
      const isCentered = Math.abs(leftSpace - rightSpace) < 10; // Allow 10px tolerance
      
      return {
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        },
        dashboard: {
          found: true,
          width: dashboardRect.width,
          left: dashboardRect.left,
          right: dashboardRect.right,
          maxWidth: dashboardStyles.maxWidth,
          margin: dashboardStyles.margin,
          padding: dashboardStyles.padding,
          position: dashboardStyles.position
        },
        mainContent: {
          found: !!mainContent,
          display: mainStyles?.display,
          justifyContent: mainStyles?.justifyContent,
          width: mainContent?.getBoundingClientRect().width,
          padding: mainStyles?.padding
        },
        body: {
          width: bodyWidth
        },
        centering: {
          leftSpace: leftSpace,
          rightSpace: rightSpace,
          isCentered: isCentered
        }
      };
    });
    
    console.log(JSON.stringify(info, null, 2));
    
    await browser.close();
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
})();