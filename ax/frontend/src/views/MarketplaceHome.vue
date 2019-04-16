<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-min='20' splitpanes-size='20'>
      <TheMarketplaceHomeDrawer></TheMarketplaceHomeDrawer>
    </div>
    <div class='ax-admin-drawer-second' splitpanes-min='50' splitpanes-size='80'>
      <TheMarketplaceHomeContent></TheMarketplaceHomeContent>
    </div>
  </splitpanes>
</template>

<script>
import TheMarketplaceHomeContent from '@/components/Marketplace/TheMarketplaceHomeContent.vue';
import TheMarketplaceHomeDrawer from '@/components/Marketplace/TheMarketplaceHomeDrawer.vue';
import Splitpanes from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

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
