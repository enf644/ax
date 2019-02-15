import Vue from 'vue';
import Router from 'vue-router';
import AdminLayout from './views/AdminLayout.vue';
import AdminHome from './views/AdminHome.vue';
import ConstructorForm from './views/ConstructorForm.vue';
import ConstructorWorkflow from './views/ConstructorWorkflow.vue';
import ConstructorGrids from './views/ConstructorGrids.vue';
import MarketplaceHome from './views/MarketplaceHome.vue';
import DeckDesigner from './views/DeckDesigner.vue';
import UsersManager from './views/UsersManager.vue';
import UsersGroup from './views/UsersGroup.vue';
import Test from './views/Test.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/admin',
      name: 'layout',
      component: AdminLayout,
      children: [
        {
          path: 'home',
          name: 'admin-home',
          component: AdminHome
        },
        {
          path: ':db_name/form',
          name: 'admin-form',
          component: ConstructorForm
        },
        {
          path: ':db_name/workflow',
          name: 'admin-workflow',
          component: ConstructorWorkflow
        },
        {
          path: ':db_name/grids/:grid_alias',
          name: 'admin-grids',
          component: ConstructorGrids
        },
        {
          path: 'users',
          name: 'users-manager',
          component: UsersManager
        },
        {
          path: 'group/:group_alias',
          name: 'users-group',
          component: UsersGroup
        },
        {
          path: 'marketplace',
          name: 'admin-marketplace',
          component: MarketplaceHome
        },
        {
          path: 'deck',
          name: 'admin-deck',
          component: DeckDesigner
        }
      ]
    },
    {
      path: '/test',
      name: 'test',
      component: Test
    }
  ]
});
