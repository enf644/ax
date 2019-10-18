import apolloClient from '../../apollo';
import gql from 'graphql-tag';
import logger from '../../logger';
import i18n from '../../locale.js';

const getDefaultState = () => {
  return {
    forms: [],
    isFormsLoaded: false,
    dbNameIsAvalible: true,
    modalMustClose: false,
    positionChangedFlag: false,
    dbNameChanged: false,
    redirectNeededUrl: null,
    redirectFromUrl: null,
    currentUser: null,
    showErrorMsg: null,
    showToastMsg: null
  }
}

const GET_ALL_FORMS = gql`
    query ($updateTime: String) {
      allForms (updateTime: $updateTime) {
        guid,
        name,
        dbName,
        isFolder,
        parent,
        position,
        icon,
        grids {
          edges {
            node {
              guid,
              name,
              dbName,
              position,
              isDefaultView
            }
          }
        },  
        tomLabel
      },
      currentAxUser (updateTime: $updateTime) {
        guid,
        email,
        shortName,
        name
      },
      allPages (updateTime: $updateTime) {
        guid,
        name,
        dbName,
        parent,
        position
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
      $defaultDelete: String!,
      $defaultDeleted: String!,
      $deleteConfirm: String!,
      $defaultUpdate: String!
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
        defaultDelete: $defaultDelete,
        defaultDeleted: $defaultDeleted,
        deleteConfirm: $deleteConfirm,
        defaultUpdate: $defaultUpdate
      ) {
      form {
        guid,
        name,
        dbName,
        isFolder,
        parent,
        position,
        icon,
        grids {
          edges {
            node {
              guid,
              name,
              dbName,
              position,
              isDefaultView
            }
          }
        },        
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
  resetState(state) {
    Object.assign(state, getDefaultState())
  },
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
  setRedirectNeededUrl(state, url) {
    state.redirectNeededUrl = url;
  },
  setRedirectFromUrl(state, url) {
    state.redirectFromUrl = url;
  },
  addGrid(state, grid) {
    state.forms.forEach(form => {
      if (form.guid === grid.formGuid) {
        form.grids.edges.push({
          node: grid
        });
      }
    });
  },
  deleteGrid(state, deleted) {
    for (let i = 0; i < state.forms.length; i += 1) {
      state.forms[i].grids.edges = [
        ...state.forms[i].grids.edges.filter(edge => edge.node.guid !== deleted)
      ];
    }
  },
  updateGrid(state, grid) {
    for (let i = 0; i < state.forms.length; i += 1) {
      if (state.forms[i].guid === grid.formGuid) {
        state.forms[i].grids.edges = [
          ...state.forms[i].grids.edges.filter(edge => edge.node.guid !== grid.guid),
          { node: grid }
        ];

        if (grid.isDefaultView) {
          for (let x = 0; x < state.forms[i].grids.edges.length; x += 1) {
            if (state.forms[i].grids.edges[x].node.guid !== grid.guid) {
              state.forms[i].grids.edges[x].node.isDefaultView = false;
            }
          }
        }
      }
    }
  },
  setShowErrorMsg(state, msg) {
    state.showErrorMsg = msg;
  },
  setShowToastMsg(state, msg) {
    state.showToastMsg = msg;
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
  },
  explorerTreeData(state) {
    const treeData = [];

    state.forms.forEach(form => {
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
        treeData.push(node);
      } else {
        const node = {
          id: form.guid,
          parent,
          text: `<i class="fas fa-${form.icon}"></i> ${form.name}`,
          type: 'default',
          data: {
            position: form.position,
            form: form.dbName,
            grid: 'Default'
          }
        };
        treeData.push(node);
        const grids = form.grids ? form.grids.edges.map(edge => edge.node) : null;
        // console.log(grids);
        if (grids) {
          grids.forEach(grid => {
            if (!grid.isDefaultView) {
              const gridNode = {
                id: grid.guid,
                parent: form.guid,
                text: `${grid.name}`,
                type: 'default',
                data: {
                  position: form.position,
                  form: form.dbName,
                  grid: grid.dbName
                }
              };
              treeData.push(gridNode);
            }
          });
        }
      }
    });
    // console.log(treeData);
    return treeData;
  }
};

const actions = {
  getAllForms({ commit, dispatch }) {
    apolloClient.query({
      query: GET_ALL_FORMS,
      variables: {
        updateTime: Date.now()
      }
    })
      .then(data => {
        commit('setForms', data.data.allForms);
        commit('users/setCurrentUser', data.data.currentAxUser, { root: true });
        commit('pages/setPages', data.data.allPages, { root: true });

      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in getAllForms apollo client -> ${error}`,
          { root: true });

        setTimeout(() => {
          dispatch('auth/goToPages', null, { root: true });
        }, 2000);
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
        defaultDeleted: i18n.tc('home.new-form.default-deleted'),
        defaultCreate: i18n.tc('home.new-form.default-create'),
        defaultState: i18n.tc('home.new-form.default-state'),
        defaultDelete: i18n.tc('home.new-form.default-delete'),
        defaultUpdate: i18n.tc('workflow.action.new-self-action-dummy'),
        deleteConfirm: i18n.tc('workflow.delete-confirm')
      }
    })
      .then(data => {
        const isDbNameAvalible = data.data.createForm.avalible;
        if (isDbNameAvalible) {
          const newForm = data.data.createForm.form;
          context.commit('addForm', newForm);
          context.commit('setModalMustClose', true);
          context.commit('setRedirectNeededUrl', `/admin/${newForm.dbName}/form`);
        } else {
          context.commit('setDbNameIsAvalible', false);
        }
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in createForm apollo client => ${error}`,
          { root: true });
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
        const msg = `Error in updateForm apollo client => ${error}`
        context.commit('home/setShowErrorMsg', msg, { root: true });
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
        context.commit('form/setFormData', null, { root: true });
        context.commit('setModalMustClose', true);
        const url = '/admin/home';
        context.commit('home/setRedirectNeededUrl', url, { root: true });
        apolloClient.resetStore();
      })
      .catch(error => {
        const msg = `Error in deleteForm apollo client => ${error}`
        context.commit('home/setShowErrorMsg', msg, { root: true });
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
        const msg = `Error in createFolder apollo client => ${error}`
        context.commit('home/setShowErrorMsg', msg, { root: true });
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
        const msg = `Error in updateFolder apollo client => ${error}`
        context.commit('home/setShowErrorMsg', msg, { root: true });
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
        const msg = `Error in deleteFolder apollo client => ${error}`
        context.commit('home/setShowErrorMsg', msg, { root: true });
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
        const msg = `Error in changeFormsPositions apollo client => ${error}`
        context.commit('home/setShowErrorMsg', msg, { root: true });
      });
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
