#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'fs';

const FILE_PATH = 'docs/.vitepress/theme/components/SOFADashboard.vue';
const CARD_MAPPINGS = [
  { id: 'other-platforms', search: 'title="Other Platforms"' },
  { id: 'safari', search: 'title="Safari Updates"' },
  { id: 'community-1', search: 'title="MacAdmins Community"' },
  { id: 'macos-feed', search: 'title="macOS Data Feed"' },
  { id: 'ios-feed', search: 'title="iOS Data Feed"' },
  { id: 'last-updated', search: 'title="Last Updated"' },
  { id: 'statistics', search: 'title="Data Statistics"' },
  { id: 'beta-releases', search: 'title="Apple Beta Releases"' },
  { id: 'timeline', search: 'title="Recent Security Releases"' },
  { id: 'community-2', search: 'title="MacAdmins Community"' }
];

console.log('🔧 Adding CSS ordering to all BentoCards...');

let content = readFileSync(FILE_PATH, 'utf8');

CARD_MAPPINGS.forEach(({ id, search }) => {
  const searchPattern = new RegExp(`(<BentoCard\\s+[^>]*${search.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[^>]*)(>)`, 'g');
  
  content = content.replace(searchPattern, (match, cardStart, closingBracket) => {
    // Check if already has style attribute
    if (cardStart.includes(':style=')) {
      console.log(`⚠️  Skipping ${id} - already has :style attribute`);
      return match;
    }
    
    console.log(`✅ Adding ordering to ${id}`);
    return `${cardStart}\n        :style="{ '--bento-order': bentoOrder.indexOf('${id}') }"${closingBracket}`;
  });
});

writeFileSync(FILE_PATH, content);
console.log('✅ All BentoCard ordering added successfully!');