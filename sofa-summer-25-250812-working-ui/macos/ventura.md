---
title: Ventura 13
platform: macOS
layout: doc
---

<script setup>
import LatestFeatures from '@components/LatestFeatures.vue'
import SecurityInfo from '@components/SecurityInfo.vue'
import LinksComponent from '@components/LinksComponent.vue'
import linksData from '@v1/essential_links.json'
</script>

# macOS Ventura 13

<LatestFeatures 
  title="Ventura 13" 
  platform="macOS"
  dataPath="/v1/macos_data_feed.json" 
  linksData="/v1/essential_links.json"
/>

<SecurityInfo 
  title="Ventura 13" 
  platform="macOS"
  dataPath="/v1/macos_data_feed.json"
/>

## Essential Resources

<LinksComponent
  title="Ventura 13"
  platform="macOS"
  :linksData="linksData"
/>