// import apolloClient from '../../apollo';
// import gql from 'graphql-tag';
// import logger from '../../logger';

const mutations = {
  increment(state) {
    state.count += 1;
    return state;
  }
};

const getters = {};
const actions = {

};

const state = {

};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
