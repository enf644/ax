<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-default='20' splitpanes-min='20'>
      <TheMarketplaceHomeDrawer></TheMarketplaceHomeDrawer>
    </div>
    <div class='ax-admin-drawer-second' splitpanes-default='80' splitpanes-min='50'>
      <TheMarketplaceHomeContent></TheMarketplaceHomeContent>
    </div>
  </splitpanes>
</template>

<script>
import TheMarketplaceHomeContent from '@/components/Marketplace/TheMarketplaceHomeContent.vue';
import TheMarketplaceHomeDrawer from '@/components/Marketplace/TheMarketplaceHomeDrawer.vue';
import Splitpanes from 'splitpanes';

export default {
  name: 'marketplace-home',
  components: {
    TheMarketplaceHomeContent,
    TheMarketplaceHomeDrawer,
    Splitpanes
  }
};
</script>

<style scoped>
</style>
