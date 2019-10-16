<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-min='20' splitpanes-size='20'>
      <TheHomeDrawer />
    </div>
    <div class='ax-admin-content-pane' splitpanes-min='30' splitpanes-size='80'>
      <TheHomeContent />
    </div>
  </splitpanes>
</template>


<script>
// import axios from 'axios';
import Splitpanes from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';
import TheHomeDrawer from '@/components/AdminHome/TheHomeDrawer.vue';
import TheHomeContent from '@/components/AdminHome/TheHomeContent.vue';

export default {
  name: 'AdminHome',
  components: {
    Splitpanes,
    TheHomeDrawer,
    TheHomeContent
  },
  data: () => ({}),
  props: {
    source: String
  },
  methods: {},
  created() {}
};
</script>

<style scoped>
</style>
