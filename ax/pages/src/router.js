import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';
import PagesSignin from './views/PagesSignin.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/signin',
      name: 'pages-signin',
      component: PagesSignin
    },
    {
      path: '/',
      name: 'home-default',
      component: Home
    },
    {
      path: '/:page',
      name: 'home',
      component: Home
    }
  ]
});
