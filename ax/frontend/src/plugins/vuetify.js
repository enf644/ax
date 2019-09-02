import Vue from 'vue';
// import Vuetify from 'vuetify/lib';
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
  VBtn
} from 'vuetify/lib';

Vue.use(Vuetify, {
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
    VBtn
  }
});

export default new Vuetify({
  // theme: {
  //   options: {
  //     customProperties: true
  //   },
  //   themes: {
  //     light: {
  //       primary: '#ee44aa',
  //       secondary: '#424242',
  //       accent: '#82B1FF',
  //       error: '#FF5252',
  //       info: '#2196F3',
  //       success: '#4CAF50',
  //       warning: '#FFC107'
  //     }
  //   }
  // },
  icons: {
    iconfont: 'fa'
  }
});
