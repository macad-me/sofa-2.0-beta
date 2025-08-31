import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  await page.goto('http://localhost:5175/sofa-2.0/', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 2000));
  
  const timeline = await page.evaluate(() => {
    const results = [];
    
    // Find the Recent Security Releases card
    document.querySelectorAll('.bento-card').forEach(card => {
      const title = card.getAttribute('title') || card.querySelector('h3')?.textContent || 'Unknown';
      if (title.includes('Recent Security Releases')) {
        // Get all timeline items
        card.querySelectorAll('.group\\/btn').forEach(item => {
          const date = item.querySelector('.text-xs.text-gray-500')?.textContent?.trim();
          const name = item.querySelector('.text-sm.font-bold')?.textContent?.trim();
          const version = item.querySelector('.text-xs.text-gray-600')?.textContent?.trim();
          
          if (name) {
            results.push({
              date,
              name,
              version
            });
          }
        });
      }
    });
    
    return results;
  });
  
  console.log('=== Recent Releases Timeline ===');
  console.log(JSON.stringify(timeline, null, 2));
  
  await browser.close();
})();