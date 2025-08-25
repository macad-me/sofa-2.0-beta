const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  
  await page.goto('http://localhost:5173/sofa-web-ui-preview/', { 
    waitUntil: 'networkidle0',
    timeout: 10000 
  });
  
  // Scroll to bottom to see footer
  await page.evaluate(() => {
    window.scrollTo(0, document.body.scrollHeight);
  });
  
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const footerInfo = await page.evaluate(() => {
    const footer = document.querySelector('.VPFooter');
    const body = document.body;
    
    if (!footer) {
      return { error: 'Footer not found' };
    }
    
    const footerRect = footer.getBoundingClientRect();
    const footerStyles = window.getComputedStyle(footer);
    const bodyWidth = body.getBoundingClientRect().width;
    
    // Check footer container
    const footerContainer = footer.querySelector('.container');
    const containerRect = footerContainer ? footerContainer.getBoundingClientRect() : null;
    const containerStyles = footerContainer ? window.getComputedStyle(footerContainer) : null;
    
    // Calculate if centered
    const leftSpace = containerRect ? containerRect.left : footerRect.left;
    const rightSpace = containerRect ? bodyWidth - containerRect.right : bodyWidth - footerRect.right;
    const isCentered = Math.abs(leftSpace - rightSpace) < 10;
    
    return {
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      footer: {
        found: true,
        width: footerRect.width,
        left: footerRect.left,
        right: footerRect.right,
        display: footerStyles.display,
        justifyContent: footerStyles.justifyContent
      },
      container: containerRect ? {
        found: true,
        width: containerRect.width,
        left: containerRect.left,
        right: containerRect.right,
        maxWidth: containerStyles.maxWidth,
        margin: containerStyles.margin
      } : { found: false },
      centering: {
        leftSpace: leftSpace,
        rightSpace: rightSpace,
        isCentered: isCentered
      }
    };
  });
  
  console.log(JSON.stringify(footerInfo, null, 2));
  
  await browser.close();
})();