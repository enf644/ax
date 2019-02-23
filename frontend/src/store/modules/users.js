import apolloClient from '../apollo';
import gql from 'graphql-tag';

const getters = {};

const actions = {
  getAllUsers({ commit }) {
    apolloClient.query({
      query: gql`
        query {
          allUsers {
            name,
            email,
            username
          }
        }
      `
    })
      .then(data => {
        console.log(data);
        commit('setUsers', data.data.allUsers);
      })
      .catch(error => console.error(error));
  }
};

const mutations = {
  setUsers(state, users) {
    state.all = users;
  }
};

const state = {
  all: ['Misha']
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
