// Core dependencies

import Vue from 'vue';
import vueCustomElement from 'vue-custom-element'; // create web component from vue component
import 'document-register-element'; // polyfill for vue-custom-element
import 'animate.css/animate.min.css';
import logger from './logger';
import './assets/ax-core.css'; // TODO check if ./ needed
import VModal from 'vue-js-modal';

// Admin dependencies
import VueResize from 'vue-resize'; // detect element resize
import '@fortawesome/fontawesome-free/css/all.css';
import 'roboto-fontface/css/roboto/roboto-fontface.css';

import AsyncComputed from 'vue-async-computed';

import 'vue-resize/dist/vue-resize.css';
import Vuetify, {
  VTextField,
  VSnackbar,
  VDialog,
  VCard,
  VToolbar,
  VIcon,
  VToolbarTitle,
  VCardText,
  VCardTitle,
  VCardActions,
  VSpacer,
  VBtn,
  VAutocomplete,
  VSelect
} from 'vuetify/lib';
import en from 'vuetify/lib/locale/en'


import VuetifyDialog from 'vuetify-dialog';
import 'vuetify-dialog/dist/vuetify-dialog.css';
import App from './App.vue';
import router from './router';
import i18n from './locale.js';

import VueCookies from 'vue-cookies'

Vue.use(VueCookies)
VueCookies.config('7d')

import VueMask from 'v-mask'

import store from './store';
import AxTest from './components/AxTest.vue';
import Fingerprint2 from 'fingerprintjs2'
import { uuidWithDashes } from '@/misc';

Vue.config.productionTip = false;

Vue.use(VueMask);

// Getting hostname of server from src of included script
// no matter how many scripts a page contains,
// the one currently starting to execute is the last one;

Vue.use(VModal, { dynamic: true, injectModalsContainer: true });

Vue.use(Vuetify, {
  lang: {
    locales: { en },
    current: 'en'
  },
  components: {
    VTextField,
    VSnackbar,
    VDialog,
    VCard,
    VCardTitle,
    VToolbar,
    VIcon,
    VToolbarTitle,
    VCardText,
    VCardActions,
    VSpacer,
    VBtn,
    VSelect,
    VAutocomplete
  }
});
Vue.use(vueCustomElement);
Vue.use(VueResize);
Vue.use(AsyncComputed);

const vuetify = new Vuetify({
  icons: { iconfont: 'fa' }
});


const gridPromise = () => import(/* webpackChunkName: "ax-grid" */ './components/AxGrid.vue').then(m => {
  return {
    ...m.default,
    vuetify
  }
});
Vue.customElement('ax-grid', gridPromise,
  {
    props: ['form', 'grid', 'update_time', 'arguments', 'width', 'height']
  }
);

const formPromise = () => import(/* webpackChunkName: "ax-form" */ './components/AxForm.vue').then(m => {
  return {
    ...m.default,
    vuetify
  }
});
Vue.customElement('ax-form', formPromise, { props: ['db_name', 'row_guid', 'update_time', 'opened_tab'] });

Vue.use(VuetifyDialog, {
  context: { vuetify },
  toast: { position: 'bottom-right' }
});

Vue.prototype.$log = logger; // Custom logger

// Write device guid using fingerprintjs. Used in sanic-jwt to enable
// user login in multiple devices
setTimeout(function () {
  const fpOptions = {
    excludeAdBlock: true
  }
  Fingerprint2.getPromise(fpOptions).then(components => {
    const values = components.map(function (component) { return component.value })
    const murmur = Fingerprint2.x64hash128(values.join(''), 31)
    const deviceGuid = uuidWithDashes(murmur);
    window.axDeviceGuid = deviceGuid
  })
}, 500)

new Vue({
  router,
  store,
  vuetify,
  i18n,
  render: h => h(App)
}).$mount('#ax-app');



const echoFunc = msg => {
  console.log(msg)
  return msg;
};

AxTest.echo = echoFunc;
AxTest.translation = { a: 'b' }
AxTest.propD = 'works works';

Vue.customElement('ax-test', {
  ...AxTest,
  vuetify
});