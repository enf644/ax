// Core dependencies
import Vue from 'vue';
import vueCustomElement from 'vue-custom-element'; // create web component from vue component
import 'document-register-element'; // polyfill for vue-custom-element
import 'roboto-fontface-woff/css/roboto-condensed/roboto-condensed-fontface.css';
import 'animate.css/animate.min.css';
import VueI18n from 'vue-i18n';
import { languages, defaultLocale } from './locale/index.js';
import logger from './logger';
import './assets/ax-core.css';
import VModal from 'vue-js-modal';

// Admin dependencies
import App from './App.vue';
import router from './router';
import store from './store';
import VueResize from 'vue-resize'; // detect element resize
import 'vue-resize/dist/vue-resize.css';
import Vuetify from 'vuetify/lib';
import 'vuetify/src/stylus/app.styl';
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { fas } from '@fortawesome/free-solid-svg-icons';

// Dev dependencies
import VueDummy from 'vue-dummy'; // create lorum ipsum

const messages = Object.assign(languages);

Vue.component('font-awesome-icon', FontAwesomeIcon);
library.add(fas);

Vue.use(VModal, { dynamic: true, injectModalsContainer: true });
Vue.use(VueI18n);
Vue.use(Vuetify, {
  components: {},
  iconfont: 'faSvg',
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

const gridPromise = () => import(/* webpackChunkName: "ax-grid" */ './components/AxGrid.vue').then(m => m.default);
Vue.customElement('ax-grid', gridPromise, { props: ['name'] });

const formPromise = () => import(/* webpackChunkName: "ax-form" */ './components/AxForm.vue').then(m => m.default);
Vue.customElement('ax-form', formPromise, {});

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
