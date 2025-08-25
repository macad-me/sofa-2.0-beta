---
title: Sonoma 14
platform: macOS
layout: doc
---

<script setup>
import LatestFeatures from '../.vitepress/theme/components/LatestFeatures.vue'
import SecurityInfo from '../.vitepress/theme/components/SecurityInfo.vue'
import LinksComponent from '../.vitepress/theme/components/LinksComponent.vue'
import linksData from '@v1/essential_links.json'
</script>

# macOS Sonoma 14

<LatestFeatures 
  title="Sonoma 14" 
  platform="macOS"
  dataPath="/v1/macos_data_feed.json" 
  linksData="/v1/essential_links.json"
/>

<SecurityInfo 
  title="Sonoma 14" 
  platform="macOS"
  dataPath="/v1/macos_data_feed.json"
/>

## Essential Resources

<LinksComponent
  title="Sonoma 14"
  platform="macOS"
  :linksData="linksData"
/>