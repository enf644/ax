import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import './registerServiceWorker';
import '@fortawesome/fontawesome-free/css/all.css';
// import 'roboto-fontface/css/roboto/roboto-fontface.css';
// import '@/assets/tailwind.css';
import '@/assets/pages-core.css';
import VueCookies from 'vue-cookies';
import i18n from './locale.js';
import Fingerprint2 from 'fingerprintjs2';
import { uuidWithDashes } from '@/misc';
import DrawerLayout from 'vue-drawer-layout';
import VueResize from 'vue-resize';
import LiquorTree from 'liquor-tree';
import VModal from 'vue-js-modal';

Vue.use(VModal, { dynamic: true, injectModalsContainer: true });
Vue.component(LiquorTree.name, LiquorTree);
Vue.use(VueResize);
Vue.use(DrawerLayout);
Vue.use(VueCookies);
VueCookies.config('7d');

Vue.config.productionTip = false;

// Write device guid using fingerprintjs. Used in sanic-jwt to enable
// user login in multiple devices
setTimeout(() => {
  const fpOptions = {
    excludeAdBlock: true
  };
  Fingerprint2.getPromise(fpOptions).then(components => {
    const values = components.map(component => component.value);
    const murmur = Fingerprint2.x64hash128(values.join(''), 31);
    const deviceGuid = uuidWithDashes(murmur);
    window.axDeviceGuid = deviceGuid;
  });
}, 100);

new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app');
