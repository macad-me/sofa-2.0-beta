---
title: visionOS 2
platform: visionOS
layout: doc
---

<script setup>
import LatestFeatures from '../../.vitepress/theme/components/LatestFeatures.vue'
import SecurityInfo from '../../.vitepress/theme/components/SecurityInfo.vue'
import LinksComponent from '../../.vitepress/theme/components/LinksComponent.vue'
import linksData from '@v1/essential_links.json'
</script>

# visionOS 2

<LatestFeatures 
  title="visionOS 2" 
  platform="visionOS"
  dataPath="/v1/visionos_data_feed.json"
  linksData="/v1/essential_links.json"
/>

<SecurityInfo 
  title="visionOS 2" 
  platform="visionOS" 
  dataPath="/v1/visionos_data_feed.json" 
/>

## Essential Resources

<LinksComponent
  title="visionOS 2"
  platform="visionOS"
  :linksData="linksData"
/>
