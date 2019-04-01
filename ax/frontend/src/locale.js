import Vue from 'vue';
import VueI18n from 'vue-i18n';
import { languages, defaultLocale } from './locale/index.js';

Vue.use(VueI18n);

const messages = Object.assign(languages);

const i18n = new VueI18n({
  locale: defaultLocale,
  fallbackLocale: 'en',
  messages
});

export default i18n;
