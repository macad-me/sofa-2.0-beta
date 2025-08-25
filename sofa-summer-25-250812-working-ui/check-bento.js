const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  
  await page.goto('http://localhost:5173/sofa-web-ui-preview/', { 
    waitUntil: 'networkidle0'
  });
  
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  const bentoInfo = await page.evaluate(() => {
    const bentoGrid = document.querySelector('.bento-grid');
    const bentoCards = document.querySelectorAll('.bento-card');
    
    return {
      gridFound: !!bentoGrid,
      cardCount: bentoCards.length,
      firstCardTitle: bentoCards[0]?.querySelector('.bento-card-title')?.textContent,
      lastCardTitle: bentoCards[bentoCards.length-1]?.querySelector('.bento-card-title')?.textContent,
      gridDisplay: bentoGrid ? window.getComputedStyle(bentoGrid).display : null,
      gridColumns: bentoGrid ? window.getComputedStyle(bentoGrid).gridTemplateColumns : null,
      gridWidth: bentoGrid ? bentoGrid.getBoundingClientRect().width : null
    };
  });
  
  console.log(JSON.stringify(bentoInfo, null, 2));
  await browser.close();
})();