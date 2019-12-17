import apolloClient from '../../apollo';
import gql from 'graphql-tag';
import logger from '../../logger';
import { getAxHostProtocol } from '@/misc';

const getDefaultState = () => {
  return {
    accessToken: window.$cookies.get('access_token'),
    refreshToken: window.$cookies.get('refresh_token')
  }
}

const LOGOUT = gql`
  mutation {
    logoutUser {
      ok    
    }
  }
`;

const getters = {};

const actions = {
  logOut(context) {
    const host = getAxHostProtocol();
    window.location.href = `${host}/api/signout?to_admin=1`;
  },
  goToPages(context) {
    const host = getAxHostProtocol();
    // console.log('auth -> goToPages');
    window.location.href = `${host}/pages/`;
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
