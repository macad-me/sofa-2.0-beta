import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  await page.goto('http://localhost:5175/sofa-2.0/', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 2000));
  
  const cards = await page.evaluate(() => {
    const results = {};
    
    // Find each specific card by its title
    document.querySelectorAll('.bento-card').forEach(card => {
      const title = card.getAttribute('title') || card.querySelector('h3')?.textContent || 'Unknown';
      const cardData = {
        versions: [],
        builds: []
      };
      
      // Get all version displays in this card
      card.querySelectorAll('.text-base.font-bold, .text-lg.font-bold').forEach(el => {
        const text = el.textContent.trim();
        if (text.includes('iOS') || text.includes('macOS') || text.includes('tvOS') || text.includes('watchOS') || text.includes('visionOS') || text.includes('Safari')) {
          cardData.versions.push(text);
        }
      });
      
      // Get builds
      card.querySelectorAll('.text-xs, .text-sm').forEach(el => {
        const text = el.textContent.trim();
        if (text.startsWith('Build ')) {
          cardData.builds.push(text);
        }
      });
      
      if (cardData.versions.length > 0 || cardData.builds.length > 0) {
        results[title] = cardData;
      }
    });
    
    return results;
  });
  
  console.log('=== Content by Card ===');
  console.log(JSON.stringify(cards, null, 2));
  
  await browser.close();
})();
