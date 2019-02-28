import apolloClient from '../../apollo';
import gql from 'graphql-tag';
import logger from '../../logger';

const SUBSCRIPTION_QUERY = gql`
    subscription {
      mutationExample {
        name,
        email
      }
    }
`;


const GET_ALL_USERS_QUERY = gql`
    query {
      allUsers {
        name,
        email,
        username
      }
    }
`;

const CREATE_NEW_USER_QUERY = gql`
  mutation ($name: String!, $email: String!, $username: String!) {
    createUser(name: $name, email: $email, username: $username) {
      user {
        uuid,
        name,
        email,
        username
      }
      ok
    }
  }
`;


const getters = {};

const actions = {
  getAllUsers({ commit }) {
    apolloClient.query({
      query: GET_ALL_USERS_QUERY,
      variables: {}
    })
      .then(data => {
        logger.info(data);
        commit('setUsers', data.data.allUsers);
      })
      .catch(error => {
        logger.error('Error in getAllUsers gql');
        logger.error(error);
      });
  },
  createNewUser() {
    apolloClient.mutate({
      mutation: CREATE_NEW_USER_QUERY,
      variables: { name: 'Jhony', email: 'jhony@dot.ru', username: 'ddha' }
    })
      .then(data => {
        logger.info(data);
      })
      .catch(error => {
        logger.error(`Error in createNewUser gql => ${error}`);
        logger.error(error);
      });
  },
  subscribeToUsers({ commit }) {
    apolloClient.subscribe({
      query: SUBSCRIPTION_QUERY,
      variables: { repoFullName: 'repoName' }
    }).subscribe({
      next(data) {
        logger.info(data);

        const newUser = {
          name: data.data.mutationExample.name,
          email: data.data.mutationExample.email
        };
        commit('addUser', newUser);
      }
    }, {
      error(error) { logger.error(`ERRROR in GQL subscribeToUsers => ${error}`); }
    });
  }
};

const mutations = {
  setUsers(state, users) {
    state.all = users;
  },
  addUser(state, userData) {
    const newUser = {
      name: userData.name,
      email: userData.email
    };
    state.all.push(newUser);
  }
};


const state = {
  all: []
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
