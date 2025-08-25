---
title: Safari 18
platform: safari
layout: doc
---

<script setup>
import LatestFeatures from '@components/LatestFeatures.vue'
import SecurityInfo from '@components/SecurityInfo.vue'
import LinksComponent from '@components/LinksComponent.vue'
import linksData from '@v1/essential_links.json'
</script>

# Safari 18

<LatestFeatures 
  title="Safari 18" 
  platform="safari"
  dataPath="/v1/safari_data_feed.json"
/>

<SecurityInfo 
  title="Safari 18" 
  platform="safari"
  dataPath="/v1/safari_data_feed.json"
/>

## Essential Resources

<LinksComponent
  title="Safari 18"
  platform="Safari"
  :linksData="linksData"
/>
