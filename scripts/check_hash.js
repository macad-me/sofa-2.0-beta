import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  await page.goto('http://localhost:5175/sofa-2.0/', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 2000));
  
  const hashInfo = await page.evaluate(() => {
    const results = {};
    
    // Find the macOS Data Feed card
    document.querySelectorAll('.bento-card').forEach(card => {
      const title = card.getAttribute('title') || card.querySelector('h3')?.textContent || 'Unknown';
      if (title.includes('macOS Data Feed')) {
        // Find the hash display
        const hashElement = card.querySelector('.font-mono.text-blue-700, .font-mono.text-blue-300');
        if (hashElement) {
          results.displayed = hashElement.textContent.trim();
          results.fullHash = hashElement.getAttribute('title');
        }
      }
      if (title.includes('iOS Data Feed')) {
        // Find the hash display
        const hashElement = card.querySelector('.font-mono.text-purple-700, .font-mono.text-purple-300');
        if (hashElement) {
          results.iosDisplayed = hashElement.textContent.trim();
          results.iosFullHash = hashElement.getAttribute('title');
        }
      }
    });
    
    return results;
  });
  
  console.log('=== Hash Display ===');
  console.log('macOS Hash (displayed):', hashInfo.displayed);
  console.log('macOS Hash (full):', hashInfo.fullHash);
  console.log('iOS Hash (displayed):', hashInfo.iosDisplayed);
  console.log('iOS Hash (full):', hashInfo.iosFullHash);
  
  // Verify against actual data (v2 feeds)
  const response = await fetch('http://localhost:5175/sofa-2.0/v2/macos_data_feed.json');
  const data = await response.json();
  console.log('\n=== Actual v2 Feed Data ===');
  console.log('macOS UpdateHash from v2 feed:', data.UpdateHash);
  
  const iosResponse = await fetch('http://localhost:5175/sofa-2.0/v2/ios_data_feed.json');
  const iosData = await iosResponse.json();
  console.log('iOS UpdateHash from v2 feed:', iosData.UpdateHash);
  
  await browser.close();
})();