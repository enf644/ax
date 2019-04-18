import apolloClient from '../../apollo';
import gql from 'graphql-tag';
import logger from '../../logger';
import i18n from '../../locale.js';

const GET_ALL_FORMS = gql`
    query {
      allForms {
        guid,
        name,
        dbName,
        isFolder,
        parent,
        position,
        icon,
        tomLabel
      }
    }
`;


const CREATE_FORM = gql`
  mutation (
      $name: String!, 
      $dbName: String!, 
      $defaultTabName: String!, 
      $defaultGridName: String!, 
      $defaultStart: String!, 
      $defaultAll: String!, 
      $defaultCreate: String!, 
      $defaultState: String!, 
      $defaultDelete: String!
    ) {
    createForm(
        name: $name, 
        dbName: $dbName, 
        defaultTabName: $defaultTabName, 
        defaultGridName: $defaultGridName,
        defaultStart: $defaultStart,
        defaultAll: $defaultAll,
        defaultCreate: $defaultCreate,
        defaultState: $defaultState,
        defaultDelete: $defaultDelete
      ) {
      form {
        guid,
        name,
        dbName,
        isFolder,
        parent,
        position,
        icon,
        tomLabel        
      },
      avalible,
      ok    
    }
  }
`;

const UPDATE_FORM = gql`
  mutation ($guid: String!, $name: String!, $dbName: String!, $icon: String!, $tomLabel: String!) {
    updateForm(guid: $guid, name: $name, dbName: $dbName, icon: $icon, tomLabel: $tomLabel) {
      form {
        guid,
        name,
        dbName,
        isFolder,
        parent,
        position,
        icon,
        tomLabel
      }
      avalible,
      dbNameChanged,
      ok    
    }
  }
`;


const DELETE_FORM = gql`
  mutation ($guid: String!) {
    deleteForm(guid: $guid) {
      forms {
        guid,
        name,
        dbName,
        isFolder,
        parent,
        position,
        icon,
        tomLabel
      },
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
        icon,
        tomLabel
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
        icon,
        tomLabel
      }
      ok    
    }
  }
`;

const DELETE_FOLDER = gql`
  mutation ($guid: String!) {
    deleteFolder(guid: $guid) {
      forms {
        guid,
        name,
        dbName,
        isFolder,
        parent,
        position,
        icon,
        tomLabel
      },
      ok    
    }
  }
`;

const CHANGE_FORMS_POSITIONS = gql`
    mutation ($positions: [PositionInput]) {
        changeFormsPositions(positions: $positions) {
          forms {
            guid,
            name,
            dbName,
            isFolder,
            parent,
            position,
            icon,
            tomLabel
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
  },
  setDbNameChanged(state, changed) {
    state.dbNameChanged = changed;
  },
  setRedirectNeeded(state, url) {
    state.redirectNeeded = url;
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
          text: `<i class="fas fa-${form.icon}"></i> ${form.name}`,
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
        logger.error(`Error in getAllForms apollo client -> ${error}`);
      });
  },
  createForm(context, payload) {
    apolloClient.mutate({
      mutation: CREATE_FORM,
      variables: {
        name: payload.name,
        dbName: payload.dbName,
        tabName: i18n.tc('home.new-form.default-tab'),
        defaultTabName: i18n.tc('home.new-form.default-tab'),
        defaultGridName: i18n.tc('home.new-form.default-grid'),
        defaultStart: i18n.tc('home.new-form.default-start'),
        defaultAll: i18n.tc('home.new-form.default-all'),
        defaultCreate: i18n.tc('home.new-form.default-create'),
        defaultState: i18n.tc('home.new-form.default-state'),
        defaultDelete: i18n.tc('home.new-form.default-delete')
      }
    })
      .then(data => {
        const isDbNameAvalible = data.data.createForm.avalible;
        if (isDbNameAvalible) {
          const newForm = data.data.createForm.form;
          context.commit('addForm', newForm);
          context.commit('setModalMustClose', true);
          context.commit('setRedirectNeeded', `/admin/${newForm.dbName}/form`);
        } else {
          context.commit('setDbNameIsAvalible', false);
        }
      })
      .catch(error => {
        logger.error(`Error in createForm apollo client => ${error}`);
      });
  },
  updateForm(context, payload) {
    apolloClient.mutate({
      mutation: UPDATE_FORM,
      variables: {
        guid: payload.guid,
        name: payload.name,
        dbName: payload.dbName,
        icon: payload.icon,
        tomLabel: payload.tomLabel
      }
    })
      .then(data => {
        const isDbNameAvalible = data.data.updateForm.avalible;
        const changed = data.data.updateForm.dbNameChanged;
        const newForm = data.data.updateForm.form;

        if (changed) {
          context.commit('updateForm', newForm);
          context.commit('setDbNameChanged', changed);
        } else if (isDbNameAvalible) {
          context.commit('updateForm', newForm);
          context.commit('setModalMustClose', true);
        } else {
          context.commit('setDbNameIsAvalible', false);
        }
      })
      .catch(error => {
        logger.error(`Error in updateForm apollo client => ${error}`);
      });
  },
  deleteForm(context, payload) {
    apolloClient.mutate({
      mutation: DELETE_FORM,
      variables: {
        guid: payload.guid
      }
    })
      .then(data => {
        context.commit('setForms', data.data.deleteForm.forms);
        context.commit('setModalMustClose', true);
        apolloClient.resetStore();
      })
      .catch(error => {
        logger.error(`Error in deleteForm apollo client => ${error}`);
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
      });
  },
  changeFormsPositions(context, payload) {
    apolloClient.mutate({
      mutation: CHANGE_FORMS_POSITIONS,
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
      });
  }
};

const state = {
  forms: [],
  isFormsLoaded: false,
  dbNameIsAvalible: true,
  modalMustClose: false,
  positionChangedFlag: false,
  dbNameChanged: false,
  redirectNeeded: null
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
