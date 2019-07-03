import Vue from 'vue';
import Router from 'vue-router';
import Test from './views/Test.vue';

const AdminLayout = () => import(/* webpackChunkName: "ax-admin" */ './views/AdminLayout.vue');
const AdminHome = () => import(/* webpackChunkName: "ax-admin" */ './views/AdminHome.vue');
const ConstructorForm = () => import(/* webpackChunkName: "ax-admin" */ './views/ConstructorForm.vue');
const ConstructorWorkflow = () => import(/* webpackChunkName: "ax-admin" */ './views/ConstructorWorkflow.vue');
const ConstructorGrids = () => import(/* webpackChunkName: "ax-admin" */ './views/ConstructorGrids.vue');
const MarketplaceHome = () => import(/* webpackChunkName: "ax-admin" */ './views/MarketplaceHome.vue');
const PagesDesigner = () => import(/* webpackChunkName: "ax-admin" */ './views/PagesDesigner.vue');
const UsersManager = () => import(/* webpackChunkName: "ax-admin" */ './views/UsersManager.vue');
const UsersGroup = () => import(/* webpackChunkName: "ax-admin" */ './views/UsersGroup.vue');

const FormView = () => import(/* webpackChunkName: "ax-form" */ './views/FormView.vue');

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
          path: 'pages',
          name: 'admin-pages',
          component: PagesDesigner
        }
      ]
    },
    {
      path: '/form/:db_name',
      name: 'form-view',
      component: FormView
    },
    {
      path: '/form/:db_name/:num_guid',
      name: 'form-view-guid',
      component: FormView
    },
    {
      path: '/test',
      name: 'test',
      component: Test
    }
  ]
});
