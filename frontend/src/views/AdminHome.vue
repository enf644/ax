<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-default='20' splitpanes-min='20'>
      <TheHomeDrawer></TheHomeDrawer>
    </div>
    <div class='ax-admin-content-pane' splitpanes-default='80' splitpanes-min='30'></div>
  </splitpanes>
</template>


<script>
import axios from 'axios';
import Splitpanes from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';
import TheHomeDrawer from '@/components/AdminHome/TheHomeDrawer.vue';

export default {
  name: 'AdminHome',
  components: {
    Splitpanes,
    TheHomeDrawer
  },
  data: () => ({}),
  props: {
    source: String
  },
  methods: {},
  created() {
    this.$log.info('running ajax');
    axios
      .get('/api/hello', {
        params: {
          object_id: 12349
        }
      })
      .then(response => {
        this.$log.info(response);
      })
      .catch(error => {
        this.$log.error(error);
      })
      .then(() => {
        // always executed
      });
  }
};
</script>

<style scoped>
</style>
