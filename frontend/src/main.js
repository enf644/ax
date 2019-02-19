import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import vueCustomElement from 'vue-custom-element'; // create web component from vue component
import 'document-register-element'; // polyfill for vue-custom-element
import Vuetify from 'vuetify'; // material ui components
import 'vuetify/dist/vuetify.min.css';
import '@fortawesome/fontawesome-free/css/all.css'; // font icons
import VueResize from 'vue-resize'; // detect element resize
import 'vue-resize/dist/vue-resize.css';
import 'typeface-roboto'; // font
import VueDummy from 'vue-dummy'; // create lorum ipsum
import 'animate.css/animate.min.css';

import '../public/static/css/ax-core.css';
import AxGrid from '@/components/AxGrid.vue';

Vue.use(Vuetify, {
  iconfont: 'fa',
  theme: {
    primary: '#3f51b5',
    secondary: '#b0bec5',
    accent: '#8c9eff',
    error: '#b71c1c'
  }
});
Vue.use(vueCustomElement);
Vue.use(VueResize);
Vue.use(VueDummy);
Vue.config.productionTip = false;
Vue.customElement('ax-grid', AxGrid);

// Logging functionality
function backendLogTransport() { } // { msg, level, args, state }

const logdown = require('logdown');

logdown.transports = [backendLogTransport];
const logger = logdown('ax');
logger.state.isEnabled = true;
Vue.prototype.$log = logger;

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app');
