import Vue from 'vue';
import vueCustomElement from 'vue-custom-element'; // create web component from vue component
import 'document-register-element'; // polyfill for vue-custom-element
import '@fortawesome/fontawesome-free/css/all.css'; // font icons
import 'typeface-roboto'; // font
import 'animate.css/animate.min.css';
import VueI18n from 'vue-i18n';
import { languages, defaultLocale } from './locale/index.js';
import logger from './logger';

import App from './App.vue';
import router from './router';
import store from './store';
import VueResize from 'vue-resize'; // detect element resize
import 'vue-resize/dist/vue-resize.css';

import Vuetify from 'vuetify/lib';
import 'vuetify/src/stylus/app.styl';

import VueDummy from 'vue-dummy'; // create lorum ipsum

import './assets/ax-core.css';
import AxGrid from './components/AxGrid.vue';

const messages = Object.assign(languages);

Vue.use(VueI18n);
Vue.use(Vuetify, {
  components: {},
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


const i18n = new VueI18n({
  locale: defaultLocale,
  fallbackLocale: 'en',
  messages
});

Vue.prototype.$log = logger; // Custom logger

new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#ax-app');
