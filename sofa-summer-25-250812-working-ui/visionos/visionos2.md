---
title: visionOS 2
platform: visionOS
layout: doc
---

<script setup>
import LatestFeatures from '@components/LatestFeatures.vue'
import SecurityInfo from '@components/SecurityInfo.vue'
import LinksComponent from '@components/LinksComponent.vue'
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
