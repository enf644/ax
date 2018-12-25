import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import vueCustomElement from 'vue-custom-element'
import AxGrid from '@/components/AxGrid.vue';
import 'document-register-element' 

Vue.use(vueCustomElement);
Vue.config.productionTip = false;

Vue.customElement('ax-grid', AxGrid);  

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount("#app");
