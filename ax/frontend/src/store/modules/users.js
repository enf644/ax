import apolloClient from '../../apollo';
import gql from 'graphql-tag';
import logger from '../../logger';

const getDefaultState = () => {
  return {
    all: [],
    groups: [],
    isUsersLoaded: false,
    currentUser: null
  }
}


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
        email
      }
    }
`;


const UPDATE_USER = gql`
  mutation ($email: String!, $name: String, $shortName: String, $password: String!, $avatarTmp: String, $info: String) {
    updateUser(email: $name, name: $email, shortName: $shortName, password: $password, avatarTmp: $avatarTmp, info: $info) {
      user {
        guid,
        email
      }
      ok
    }
  }
`;

const DELETE_USER = gql`
  mutation ($guid: String!) {
    deleteUser(guid: $guid) {
      deleted,
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
        commit('setUsers', data.data.allUsers);
      })
      .catch(error => {
        logger.error('Error in getAllUsers gql');
        logger.error(error);
      });
  }
};

const mutations = {
  resetState(state) {
    Object.assign(state, getDefaultState())
  },
  setUsers(state, users) {
    state.all = users;
    state.isUsersLoaded = true;
  },
  setGroups(state, groups) {
    state.groups = groups;
  },
  updateGroup(state, group) {
    state.groups = [
      ...state.groups.filter(element => element.guid !== group.guid),
      group
    ];
  },
  setCurrentUser(state, user) {
    state.currentUser = user;
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
