import apolloClient from '../../apollo';
import gql from 'graphql-tag';
import logger from '../../logger';

const getters = {};

const actions = {
  logOut(context) {
    window.$cookies.set('access_token', null);
    window.$cookies.set('refresh_token', null);

    context.commit('setTokens', {
      access: null,
      refresh: null
    })
  }
};

const mutations = {
  setTokens(state, payload) {
    state.accessToken = payload.access;
    state.refreshToken = payload.refresh;
  }
};


const state = {
  accessToken: window.$cookies.get('access_token'),
  refreshToken: window.$cookies.get('refresh_token')
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
