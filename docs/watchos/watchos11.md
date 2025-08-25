---
title: watchOS 11
platform: watchOS
layout: doc
---

<script setup>
import LatestFeatures from '../../.vitepress/theme/components/LatestFeatures.vue'
import SecurityInfo from '../../.vitepress/theme/components/SecurityInfo.vue'
import LinksComponent from '../../.vitepress/theme/components/LinksComponent.vue'
import linksData from '@v1/essential_links.json'
</script>

# watchOS 11

<LatestFeatures 
  title="watchOS 11" 
  platform="watchOS"
  dataPath="/v1/watchos_data_feed.json" 
  linksData="/v1/essential_links.json"
>
</LatestFeatures>

<SecurityInfo 
  title="watchOS 11" 
  platform="watchOS" 
  dataPath="/v1/watchos_data_feed.json" 
/>

## Essential Resources

<LinksComponent
  title="watchOS 11"
  platform="watchOS"
  :linksData="linksData"
/>
