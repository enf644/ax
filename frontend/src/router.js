import Vue from 'vue';
import Router from 'vue-router';
import AdminHome from './views/AdminHome.vue';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: AdminHome
    }
  ]
});
