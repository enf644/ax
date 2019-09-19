/* eslint-disable global-require */

import Vue from 'vue';
import Vuex from 'vuex';
import pages from './modules/pages';
import form from './modules/form';
import grids from './modules/grids';
import home from './modules/home';
import test from './modules/test';
import users from './modules/users';
import workflow from './modules/workflow';
import auth from './modules/auth';
import createLogger from 'vuex/dist/logger';

Vue.use(Vuex);

const debug = process.env.NODE_ENV !== 'production';

const store = new Vuex.Store({
  modules: {
    pages,
    form,
    grids,
    home,
    users,
    test,
    workflow,
    auth
  },
  strict: debug,
  plugins: debug ? [createLogger()] : []
});

if (module.hot) {
  module.hot.accept([
    './modules/pages',
    './modules/form',
    './modules/grids',
    './modules/home',
    './modules/users',
    './modules/test',
    './modules/workflow',
    './modules/auth'
  ], () => {
    const newPages = require('./modules/pages').default;
    const newForm = require('./modules/form').default;
    const newGrids = require('./modules/grids').default;
    const newHome = require('./modules/home').default;
    const newUsers = require('./modules/users').default;
    const newTest = require('./modules/test').default;
    const newWorkflow = require('./modules/workflow').default;
    const newAuth = require('./modules/auth').default;
    store.hotUpdate({
      modules: {
        pages: newPages,
        form: newForm,
        grids: newGrids,
        home: newHome,
        users: newUsers,
        test: newTest,
        workflow: newWorkflow,
        auth: newAuth
      }
    });
  });
}

export default store;
