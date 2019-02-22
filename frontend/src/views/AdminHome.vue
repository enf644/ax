<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-default='20' splitpanes-min='20'>
      <TheHomeDrawer/>
    </div>
    <div class='ax-admin-content-pane' splitpanes-default='80' splitpanes-min='30'>
      <TheHomeContent/>
    </div>
  </splitpanes>
</template>


<script>
import axios from 'axios';
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
  created() {
    const ws = new WebSocket('ws://127.0.0.1:8080/api/echo');
    ws.onopen = function sendOpenSignal() {
      this.$log.info('sent open signal');
      ws.send('socket open');
    }.bind(this);
    ws.onclose = function sendCloseSignal(evt) {
      this.$log.info(`socket closed = ${evt.data}`);
    }.bind(this);
    ws.onmessage = function onMessage(evt) {
      this.$log.info(evt.data);
    }.bind(this);

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
