import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  // Capture console logs
  const logs = [];
  page.on('console', msg => {
    if (msg.text().includes('from bulletin')) {
      logs.push(msg.text());
    }
  });
  
  console.log('Navigating to dashboard...');
  await page.goto('http://localhost:5175/sofa-2.0/', {
    waitUntil: 'networkidle2',
    timeout: 30000
  });
  
  // Wait for Vue to mount
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  console.log('\n=== Console Logs from Component ===');
  logs.forEach(log => console.log(log));
  
  // Get displayed values
  const displayed = await page.evaluate(() => {
    const text = document.body.innerText;
    const results = {};
    
    // Find specific version displays
    const macosMatches = text.match(/macOS\s+([\d.]+)[\s\S]*?Build\s+(\w+)[\s\S]*?(\d+)\s+CVEs/);
    if (macosMatches) {
      results.macOS = {
        version: macosMatches[1],
        build: macosMatches[2],
        cves: macosMatches[3]
      };
    }
    
    const iosMatches = text.match(/iOS\s+([\d.]+)[\s\S]*?Build\s+(\w+)[\s\S]*?(\d+)\s+CVEs/);
    if (iosMatches) {
      results.iOS = {
        version: iosMatches[1],
        build: iosMatches[2],
        cves: iosMatches[3]
      };
    }
    
    return results;
  });
  
  console.log('\n=== What\'s Actually Displayed ===');
  console.log(JSON.stringify(displayed, null, 2));
  
  await browser.close();
})();