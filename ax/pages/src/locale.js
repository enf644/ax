import Vue from 'vue';
import VueI18n from 'vue-i18n';
import { languages, defaultLocale } from './locale/index.js';

Vue.use(VueI18n);

const messages = Object.assign(languages);

const dateTimeFormats = {
  en: {
    short: {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    },
    normal: {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric'
    },
    long: {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      weekday: 'short',
      hour: 'numeric',
      minute: 'numeric'
    }
  },
  ja: {
    short: {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    },
    long: {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      weekday: 'short',
      hour: 'numeric',
      minute: 'numeric',
      hour12: true
    }
  }
};

const i18n = new VueI18n({
  locale: defaultLocale,
  fallbackLocale: 'en',
  messages,
  dateTimeFormats
});

export default i18n;
