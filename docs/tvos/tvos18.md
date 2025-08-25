---
title: tvOS 18
platform: tvOS
layout: doc
---

<script setup>
import LatestFeatures from '../../.vitepress/theme/components/LatestFeatures.vue'
import SecurityInfo from '../../.vitepress/theme/components/SecurityInfo.vue'
import LinksComponent from '../../.vitepress/theme/components/LinksComponent.vue'
import linksData from '@v1/essential_links.json'
</script>

# tvOS 18

<LatestFeatures 
  title="tvOS 18" 
  platform="tvOS"
  dataPath="/v1/tvos_data_feed.json" 
  linksData="/v1/essential_links.json"
>
</LatestFeatures>

<SecurityInfo 
  title="tvOS 18" 
  platform="tvOS" 
  dataPath="/v1/tvos_data_feed.json" 
/>

## Essential Resources

<LinksComponent
  title="tvOS 18"
  platform="tvOS"
  :linksData="linksData"
/>
