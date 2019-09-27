import apolloClient from '../../apollo';
import gql from 'graphql-tag';
import logger from '../../logger';

const getDefaultState = () => {
  return {
    accessToken: window.$cookies.get('access_token'),
    refreshToken: window.$cookies.get('refresh_token')
  }
}

const getters = {};

const actions = {
  logOut(context) {
    window.$cookies.set('access_token', null);
    window.$cookies.set('refresh_token', null);

    context.commit('setTokens', {
      access: null,
      refresh: null
    })

    context.commit('home/resetState', null, { root: true });
    context.commit('form/resetState', null, { root: true });
    context.commit('grids/resetState', null, { root: true });
    context.commit('workflow/resetState', null, { root: true });
    context.commit('pages/resetState', null, { root: true });
  }
};

const mutations = {
  resetState(state) {
    Object.assign(state, getDefaultState())
  },
  setTokens(state, payload) {
    state.accessToken = payload.access;
    state.refreshToken = payload.refresh;
  }
};


const state = getDefaultState();

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
