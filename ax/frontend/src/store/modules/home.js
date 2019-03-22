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


const CREATE_FOLDER = gql`
  mutation ($name: String!) {
    createFolder(name: $name) {
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


const UPDATE_FOLDER = gql`
  mutation ($guid: String!, $name: String!) {
    updateFolder(guid: $guid, name: $name) {
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

const DELETE_FOLDER = gql`
  mutation ($guid: String!) {
    updateFolder(guid: $guid) {
      forms {
        guid,
        name,
        dbName,
        isFolder,
        parent,
        position,
        icon
      },
      ok    
    }
  }
`;

const CHANGE_FROMS_POSITIONS = gql`
    mutation ($positions: [PositionInput]) {
        changeFormsPositions(positions: $positions) {
          forms {
            guid,
            name,
            dbName,
            isFolder,
            parent,
            position,
            icon
          }
        }
    }`;

const mutations = {
  setForms(state, forms) {
    state.forms = forms;
    state.isFormsLoaded = true;
  },
  addForm(state, form) {
    state.forms.push(form);
  },
  updateForm(state, form) {
    state.forms = [
      ...state.forms.filter(element => element.guid !== form.guid),
      form
    ];
  },
  deleteForm(state, guid) {
    state.forms = [...state.forms.filter(element => element.guid === guid)];
  },
  setDbNameIsAvalible(state, avalible) {
    state.dbNameIsAvalible = avalible;
  },
  setModalMustClose(state, created) {
    state.modalMustClose = created;
  },
  setPositionChangedFlag(state, changed) {
    state.positionChangedFlag = changed;
  }
};

const getters = {
  jsTreeData(state) {
    const jsTreeData = [];

    for (let i = 0; i < state.forms.length; i += 1) {
      const form = state.forms[i];
      const parent = form.parent || '#';

      if (form.isFolder) {
        const node = {
          id: form.guid,
          parent,
          text: `${form.name}`,
          type: 'folder',
          data: {
            position: form.position,
            dbName: null
          }
        };
        jsTreeData.push(node);
      } else {
        const node = {
          id: form.guid,
          parent,
          text: `<i class="far fa-${form.icon}"></i> ${form.name}`,
          type: 'default',
          data: {
            position: form.position,
            dbName: form.dbName
          }
        };
        jsTreeData.push(node);
      }
    }
    return jsTreeData;
  }
};

const actions = {
  getAllForms({ commit }) {
    apolloClient.query({
      query: GET_ALL_FORMS,
      variables: {}
    })
      .then(data => {
        commit('setForms', data.data.allForms);
      })
      .catch(error => {
        logger.error('Error in getAllForms apollo client');
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
          context.commit('setModalMustClose', true);
        } else {
          context.commit('setDbNameIsAvalible', false);
        }
      })
      .catch(error => {
        logger.error(`Error in createForm apollo client => ${error}`);
        logger.error(error);
      });
  },
  createFolder(context, payload) {
    apolloClient.mutate({
      mutation: CREATE_FOLDER,
      variables: {
        name: payload.name
      }
    })
      .then(data => {
        const newForm = data.data.createFolder.form;
        context.commit('addForm', newForm);
        context.commit('setModalMustClose', true);
      })
      .catch(error => {
        logger.error(`Error in createFolder apollo client => ${error}`);
        logger.error(error);
      });
  },
  updateFolder(context, payload) {
    apolloClient.mutate({
      mutation: UPDATE_FOLDER,
      variables: {
        guid: payload.guid,
        name: payload.name
      }
    })
      .then(data => {
        const updatedForm = data.data.updateFolder.form;
        context.commit('updateForm', updatedForm);
        context.commit('setModalMustClose', true);
      })
      .catch(error => {
        logger.error(`Error in updateFolder apollo client => ${error}`);
        logger.error(error);
      });
  },
  deleteFolder(context, payload) {
    apolloClient.mutate({
      mutation: DELETE_FOLDER,
      variables: {
        guid: payload.guid
      }
    })
      .then(data => {
        context.commit('setForms', data.data.deleteFolder.forms);
        context.commit('setModalMustClose', true);
      })
      .catch(error => {
        logger.error(`Error in deleteFolder apollo client => ${error}`);
        logger.error(error);
      });
  },
  changeFormsPositions(context, payload) {
    apolloClient.mutate({
      mutation: CHANGE_FROMS_POSITIONS,
      variables: {
        positions: payload.positions
      }
    })
      .then(data => {
        context.commit('setPositionChangedFlag', true);
        context.commit('setForms', data.data.changeFormsPositions.forms);
      })
      .catch(error => {
        logger.error(`Error in changeFormsPositions apollo client => ${error}`);
        logger.error(error);
      });
  }
};

const state = {
  forms: [],
  isFormsLoaded: false,
  dbNameIsAvalible: true,
  modalMustClose: false,
  positionChangedFlag: false
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
