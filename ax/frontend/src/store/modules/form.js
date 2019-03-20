import apolloClient from '../../apollo';
import gql from 'graphql-tag';
import logger from '../../logger';

const GET_ALL_FORMS = gql`
    query {
      allForms {
        guid,
        name,
        dbName,
        isFolder,
        parent,
        position,
        icon
      }
    }
`;

const CREATE_FORM = gql`
  mutation ($name: String!, $dbName: String!) {
    createForm(name: $name, dbName: $dbName) {
      avalible,
      form {
        guid,
        name,
        dbName,
        isFolder,
        parent,
        position,
        icon
      }
      ok    
    }
  }
`;

const mutations = {
  setForms(state, forms) {
    state.forms = forms;
  },
  addForm(state, form) {
    state.forms.push(form);
  },
  setDbNameIsAvalible(state, avalible) {
    state.dbNameIsAvalible = avalible;
  },
  setNewFormCreated(state, created) {
    state.newFormCreated = created;
  }
};

const getters = {};

const actions = {
  getAllForms({ commit }) {
    apolloClient.query({
      query: GET_ALL_FORMS,
      variables: {}
    })
      .then(data => {
        logger.info(data);
        commit('setForms', data.data.allForms);
      })
      .catch(error => {
        logger.error('Error in getAllForms gql');
        logger.error(error);
      });
  },
  createForm(context, payload) {
    apolloClient.mutate({
      mutation: CREATE_FORM,
      variables: {
        name: payload.name,
        dbName: payload.dbName
      }
    })
      .then(data => {
        const isDbNameAvalible = data.data.createForm.avalible;
        if (isDbNameAvalible) {
          const newForm = data.data.createForm.form;
          context.commit('addForm', newForm);
          context.commit('setNewFormCreated', true);
        } else {
          context.commit('setDbNameIsAvalible', false);
        }
      })
      .catch(error => {
        logger.error(`Error in createForm gql => ${error}`);
        logger.error(error);
      });
  }
};

const state = {
  forms: [],
  dbNameIsAvalible: true,
  newFormCreated: false
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
