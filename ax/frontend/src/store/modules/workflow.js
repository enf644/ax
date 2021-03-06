import apolloClient from '../../apollo';
import gql from 'graphql-tag';
import logger from '../../logger';
import i18n from '../../locale.js';

const getDefaultState = () => {
  return {
    formGuid: null,
    formDbName: null,
    roles: [],
    states: [],
    actions: [],
    currentStateGuid: [],
    permissions: [],
    updateTime: null,
    addedAction: null,
    highlightedRole: null
  }
}


const CREATE_STATE = gql`
  mutation ($formGuid: String!, $name: String!, $x: Float!, $y: Float!, $update: String) {
    createState(formGuid: $formGuid, name: $name, x: $x, y: $y, update: $update) {
      state {
        guid,
        name,
        roles{
          edges {
            node {
              guid,
              name,
              isDynamic
            }
          }
        },
        isStart,
        isDeleted,
        isAll,
        x,
        y   
      },
      action {
        guid,
        name,
        roles{
          edges {
            node {
              guid,
              name,
              isDynamic
            }
          }
        },
        fromStateGuid,
        toStateGuid,
        icon,
        radius
      },
      permissions {
        guid,
        formGuid,
        roleGuid,
        stateGuid,
        fieldGuid,
        read,
        edit        
      }  
      ok  
    }
  }
`;

const UPDATE_STATE = gql`
  mutation ($guid: String!, $name: String, $x: Float, $y: Float ) {
    updateState(guid: $guid, name: $name, x: $x, y: $y) {
      state {
        guid,
        name,
        roles{
          edges {
            node {
              guid
            }
          }
        },
        isStart,
        isDeleted,
        isAll,
        x,
        y   
      },
      ok    
    }
  }
`;

const DELETE_STATE = gql`
  mutation ($guid: String!) {
    deleteState(guid: $guid) {
      deleted,
      ok    
    }
  }
`;

const CREATE_ACTION = gql`
  mutation ($formGuid: String!, $name: String!, $fromStateGuid: String!, $toStateGuid: String!) {
    createAction(formGuid: $formGuid, name: $name, fromStateGuid: $fromStateGuid, toStateGuid: $toStateGuid) {
      action {
        guid,
        name,
        roles{
          edges {
            node {
              guid
            }
          }
        },
        fromStateGuid,
        toStateGuid,
        icon,
        radius
      },
      ok    
    }
  }
`;

const UPDATE_ACTION = gql`
  mutation ($guid: String!, $name: String, $dbName: String, $code: String, $confirmText: String, $closeModal: Boolean, $icon: String, $radius: Float ) {
    updateAction(guid: $guid, name: $name, dbName: $dbName, code: $code, confirmText: $confirmText, closeModal: $closeModal, icon: $icon, radius: $radius) {
      action {
        guid,
        name,
        dbName,
        roles{
          edges {
            node {
              guid
            }
          }
        },
        fromStateGuid,
        toStateGuid,
        icon,
        radius,
        code,
        confirmText,
        closeModal
      },
      ok    
    }
  }
`;

const DELETE_ACTION = gql`
  mutation ($guid: String!) {
    deleteAction(guid: $guid) {
      deleted,
      ok    
    }
  }
`;

const GET_ACTION_DATA = gql`
  query ($guid: String!, $updateTime: String) {
    actionData(guid: $guid, updateTime: $updateTime) {
      guid,
      name,
      dbName,
      code,
      confirmText,
      closeModal,
      roles{
        edges {
          node {
            guid,
            name
          }
        }
      },
      fromStateGuid,
      toStateGuid,
      icon,
      radius
    }
  }
`;

const CREATE_ROLE = gql`
  mutation ($formGuid: String!, $name: String!, $isDynamic: Boolean) {
    createRole(formGuid: $formGuid, name: $name, isDynamic: $isDynamic) {
      role {
        guid,
        name,
        icon,
        isDynamic
      },
      ok    
    }
  }
`;


const UPDATE_ROLE = gql`
  mutation ($guid: String!, $name: String, $icon: String, $code: String) {
    updateRole(guid: $guid, name: $name, icon: $icon, code: $code) {
      role {
        guid,
        name,
        icon,
        isDynamic
      },
      ok    
    }
  }
`;

const DELETE_ROLE = gql`
  mutation ($guid: String!) {
    deleteRole(guid: $guid) {
      deleted,
      ok    
    }
  }
`;


const ADD_ROLE_TO_STATE = gql`
  mutation ($stateGuid: String!, $roleGuid: String!) {
    addRoleToState(stateGuid: $stateGuid, roleGuid: $roleGuid) {
      state2role {
        guid,
        stateGuid,
        roleGuid
      },
      ok    
    }
  }
`;

const DELETE_ROLE_FROM_STATE = gql`
  mutation ($guid: String, $stateGuid: String, $roleGuid: String) {
    deleteRoleFromState(guid: $guid, stateGuid: $stateGuid, roleGuid: $roleGuid) {
      deleted,
      roleGuid,
      stateGuid
      ok    
    }
  }
`;

const ADD_ROLE_TO_ACTION = gql`
  mutation ($actionGuid: String!, $roleGuid: String!) {
    addRoleToAction(actionGuid: $actionGuid, roleGuid: $roleGuid) {
      action2role {
        guid,
        actionGuid,
        roleGuid
      },
      ok    
    }
  }
`;

const DELETE_ROLE_FROM_ACTION = gql`
  mutation ($guid: String, $actionGuid: String, $roleGuid: String) {
    deleteRoleFromAction(guid: $guid, actionGuid: $actionGuid, roleGuid: $roleGuid) {
      deleted,
      roleGuid,
      actionGuid,
      ok    
    }
  }
`;

const SET_STATE_PERMISSION = gql`
  mutation ($formGuid: String!, $stateGuid: String!, $roleGuid: String!, $fieldGuid: String, $read: Boolean!, $edit: Boolean!) {
    setStatePermission(formGuid: $formGuid, stateGuid: $stateGuid, roleGuid: $roleGuid, fieldGuid: $fieldGuid, read: $read, edit: $edit) {
      permissions {
        guid,
        formGuid,
        roleGuid,
        stateGuid,
        fieldGuid,
        read,
        edit
      },
      ok    
    }
  }
`;


const mutations = {
  resetState(state) {
    Object.assign(state, getDefaultState())
  },
  setWorkflowData(state, data) {
    if (data) {
      state.formGuid = data.guid;
      state.formDbName = data.dbName;
      state.roles = data.roles ? data.roles.edges.map(edge => edge.node) : null;
      state.states = data.states ? data.states.edges.map(edge => edge.node) : null;
      state.actions = data.actions ? data.actions.edges.map(edge => edge.node) : null;
      state.permissions = data.permissions ? data.permissions.edges.map(edge => edge.node) : null;
    } else {
      state.formGuid = null;
      state.formDbName = null;
      state.roles = [];
      state.states = [];
      state.actions = [];
      state.permissions = [];
    }
  },
  addState(state, newState) {
    state.states.push(newState);
  },
  updateState(state, newState) {
    state.states = [
      ...state.states.filter(element => element.guid !== newState.guid),
      newState
    ];
  },
  setStatePosition(state, newState) {
    const stateIndex = state.states.findIndex(
      axState => axState.guid === newState.guid
    );
    state.states[stateIndex].x = newState.x;
    state.states[stateIndex].y = newState.y;
  },
  deleteState(state, guid) {
    state.states = [...state.states.filter(element => element.guid !== guid)];
    state.actions = [...state.actions
      .filter(element => element.fromStateGuid !== guid && element.toStateGuid !== guid)];
  },
  addAction(state, action) {
    state.actions.push(action);
  },
  updateAction(state, action) {
    state.actions = [
      ...state.actions.filter(element => element.guid !== action.guid),
      action
    ];
  },
  updateActionRadius(state, action) {
    const index = state.actions.findIndex(
      act => act.guid === action.guid
    );
    state.actions[index].radius = action.radius;
  },
  deleteAction(state, guid) {
    state.actions = [...state.actions.filter(element => element.guid !== guid)];
  },
  setRoles(state, roles) {
    state.roles = [...roles]
  },
  addRole(state, role) {
    state.roles.push(role);
  },
  updateRole(state, role) {
    state.roles = [
      ...state.roles.filter(element => element.guid !== role.guid),
      role
    ];
  },
  deleteRole(state, guid) {
    state.roles = [...state.roles.filter(element => element.guid !== guid)];
  },
  addRoleToState(state, state2role) {
    state.states.forEach(currentState => {
      const newNode = {};
      const roleName = state.roles.find(role => role.guid === state2role.roleGuid).name;
      newNode.node = {
        guid: state2role.roleGuid,
        name: roleName
      };
      if (currentState.guid === state2role.stateGuid) currentState.roles.edges.push(newNode);
    });
  },
  deleteRoleFromState(state, state2role) {
    state.states.forEach((currentState, i) => {
      if (currentState.guid === state2role.stateGuid) {
        const filtered = currentState.roles.edges
          .filter(element => element.node.guid !== state2role.roleGuid);
        const newRoles = [...filtered];
        state.states[i].roles.edges = newRoles;
      }
    });
  },
  addRoleToAction(state, action2role) {
    state.actions.forEach(currentAction => {
      const newNode = {};
      newNode.node = { guid: action2role.roleGuid };
      if (currentAction.guid === action2role.actionGuid) currentAction.roles.edges.push(newNode);
    });
  },
  deleteRoleFromAction(state, action2role) {
    state.actions.forEach((currentAction, i) => {
      if (currentAction.guid === action2role.actionGuid) {
        const filtered = currentAction.roles.edges
          .filter(element => element.node.guid !== action2role.roleGuid);
        const newRoles = [...filtered];
        state.actions[i].roles.edges = newRoles;
      }
    });
  },
  setStatePermissions(state, statePermissions) {
    if (statePermissions[0]) {
      state.currentStateGuid = statePermissions[0].stateGuid;
      const filtered = state.permissions
        .filter(element => element.stateGuid !== state.currentStateGuid);
      const combined = filtered.concat(statePermissions);
      state.permissions = [...combined];
    }
  },
  setFieldPermissions(state, fieldPermissions) {
    if (fieldPermissions[0]) {
      const { fieldGuid } = fieldPermissions[0];
      const filtered = state.permissions
        .filter(element => element.fieldGuid !== fieldGuid);
      const combined = filtered.concat(fieldPermissions);
      state.permissions = [...combined];
    }
  },
  setAddedAction(state, action) {
    state.addedAction = action;
  },
  setHighlightedRole(state, role) {
    state.highlightedRole = role;
  }
};

const getters = {
  rolesWithColor(state) {
    let retRoles = [];
    const materialColors = [
      '#8BC34A',
      '#FFEB3B',
      '#FFC107',
      '#2196F3',
      '#FF9800',
      '#00BCD4',
      '#CDDC39',
      '#E91E63',
      '#FF5722',
      '#009688',
      '#4CAF50',
      '#9E9E9E',
      '#F44336',
      '#3F51B5',
      '#FF9800'
    ];
    state.roles.forEach(role => {
      const newRole = Object.assign({}, role);
      let index = state.roles.indexOf(role);
      while (index > materialColors.length) {
        index -= this.materialColors.length;
      }
      newRole.color = materialColors[index];
      retRoles.push(newRole);

      retRoles = retRoles.sort(function (a, b) {
        if (a.name < b.name) { return -1; }
        if (a.name > b.name) { return 1; }
        return 0;
      })
    });
    return retRoles;
  }
};
const actions = {

  createState(context, payload) {
    apolloClient.mutate({
      mutation: CREATE_STATE,
      variables: {
        formGuid: context.state.formGuid,
        name: payload.name,
        x: payload.x,
        y: payload.y,
        update: i18n.tc('workflow.action.new-self-action-dummy')
      }
    })
      .then(data => {
        const newState = data.data.createState.state;
        context.commit('addState', newState);

        const updateAction = data.data.createState.action;
        context.commit('addAction', updateAction);
        context.commit('setAddedAction', updateAction);

        const newPermissions = data.data.createState.permissions;
        context.commit('setStatePermissions', newPermissions);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in createState apollo client => ${error}`, { root: true });
      });
  },

  updateState(context, payload) {
    apolloClient.mutate({
      mutation: UPDATE_STATE,
      variables: {
        guid: payload.guid,
        name: payload.name,
        x: payload.x,
        y: payload.y
      }
    })
      .then(data => {
        const updatedState = data.data.updateState.state;
        context.commit('updateState', updatedState);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in updateState apollo client => ${error}`, { root: true });
      });
  },

  updateStatePosition(context, payload) {
    apolloClient.mutate({
      mutation: UPDATE_STATE,
      variables: {
        guid: payload.guid,
        name: null,
        x: payload.x,
        y: payload.y
      }
    })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in updateStatePosition apollo client => ${error}`, { root: true });
      });
  },

  deleteState(context, payload) {
    apolloClient.mutate({
      mutation: DELETE_STATE,
      variables: {
        guid: payload.guid
      }
    })
      .then(data => {
        const deletedGuid = data.data.deleteState.deleted;
        context.commit('deleteState', deletedGuid);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in deleteState apollo client => ${error}`, { root: true });
      });
  },

  createAction(context, payload) {
    apolloClient.mutate({
      mutation: CREATE_ACTION,
      variables: {
        formGuid: context.state.formGuid,
        name: payload.name,
        fromStateGuid: payload.fromStateGuid,
        toStateGuid: payload.toStateGuid
      }
    })
      .then(data => {
        const newAction = data.data.createAction.action;
        context.commit('addAction', newAction);
        context.commit('setAddedAction', newAction);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in createAction apollo client => ${error}`, { root: true });
      });
  },


  updateAction(context, payload) {
    apolloClient.mutate({
      mutation: UPDATE_ACTION,
      variables: {
        guid: payload.guid,
        name: payload.name,
        dbName: payload.dbName,
        code: payload.code,
        confirmText: payload.confirmText,
        closeModal: payload.closeModal,
        icon: payload.icon,
        radius: payload.radius
      }
    })
      .then(data => {
        const updatedAction = data.data.updateAction.action;
        context.commit('updateAction', updatedAction);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in updateAction apollo client => ${error}`, { root: true });
      });
  },


  updateActionRadius(context, payload) {
    apolloClient.mutate({
      mutation: UPDATE_ACTION,
      variables: {
        guid: payload.guid,
        radius: payload.radius
      }
    })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in updateActionRadius apollo client => ${error}`, { root: true });
      });
  },

  deleteAction(context, payload) {
    apolloClient.mutate({
      mutation: DELETE_ACTION,
      variables: {
        guid: payload.guid
      }
    })
      .then(data => {
        const deletedGuid = data.data.deleteAction.deleted;
        context.commit('deleteAction', deletedGuid);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in deleteAction apollo client => ${error}`, { root: true });
      });
  },

  getActionData(context, payload) {
    apolloClient.query({
      query: GET_ACTION_DATA,
      variables: {
        guid: payload.guid,
        updateTime: Date.now()
      }
    })
      .then(data => {
        const newAction = data.data.actionData;
        context.commit('updateAction', newAction);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in getActionData apollo client => ${error}`, { root: true });
      });
  },

  createRole(context, payload) {
    apolloClient.mutate({
      mutation: CREATE_ROLE,
      variables: {
        formGuid: context.state.formGuid,
        name: payload.name,
        isDynamic: payload.isDynamic
      }
    })
      .then(data => {
        const newRole = data.data.createRole.role;
        context.commit('addRole', newRole);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in createRole apollo client => ${error}`, { root: true });
      });
  },


  updateRole(context, payload) {
    apolloClient.mutate({
      mutation: UPDATE_ROLE,
      variables: {
        guid: payload.guid,
        name: payload.name,
        icon: payload.icon,
        code: payload.code
      }
    })
      .then(data => {
        const newRole = data.data.updateRole.role;
        context.commit('updateRole', newRole);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in updateRole apollo client => ${error}`, { root: true });
      });
  },

  deleteRole(context, payload) {
    apolloClient.mutate({
      mutation: DELETE_ROLE,
      variables: {
        guid: payload.guid
      }
    })
      .then(data => {
        const { deleted } = data.data.deleteRole;
        context.commit('deleteRole', deleted);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in deleteRole apollo client => ${error}`, { root: true });
      });
  },

  addRoleToState(context, payload) {
    apolloClient.mutate({
      mutation: ADD_ROLE_TO_STATE,
      variables: {
        stateGuid: payload.stateGuid,
        roleGuid: payload.roleGuid
      }
    })
      .then(data => {
        const { state2role } = data.data.addRoleToState;
        context.commit('addRoleToState', state2role);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in addRoleToState apollo client => ${error}`, { root: true });
      });
  },

  deleteRoleFromState(context, payload) {
    apolloClient.mutate({
      mutation: DELETE_ROLE_FROM_STATE,
      variables: {
        stateGuid: payload.stateGuid,
        roleGuid: payload.roleGuid
      }
    })
      .then(data => {
        const deletedGuid = data.data.deleteRoleFromState.deleted;
        const { roleGuid } = data.data.deleteRoleFromState;
        const { stateGuid } = data.data.deleteRoleFromState;
        const state2role = {
          guid: deletedGuid,
          roleGuid,
          stateGuid
        };
        context.commit('deleteRoleFromState', state2role);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in deleteRoleFromState apollo client => ${error}`, { root: true });
      });
  },

  addRoleToAction(context, payload) {
    apolloClient.mutate({
      mutation: ADD_ROLE_TO_ACTION,
      variables: {
        actionGuid: payload.actionGuid,
        roleGuid: payload.roleGuid
      }
    })
      .then(data => {
        const { action2role } = data.data.addRoleToAction;
        context.commit('addRoleToAction', action2role);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in addRoleToAction apollo client => ${error}`, { root: true });
      });
  },

  deleteRoleFromAction(context, payload) {
    apolloClient.mutate({
      mutation: DELETE_ROLE_FROM_ACTION,
      variables: {
        actionGuid: payload.actionGuid,
        roleGuid: payload.roleGuid
      }
    })
      .then(data => {
        const deletedGuid = data.data.deleteRoleFromAction.deleted;
        const { roleGuid } = data.data.deleteRoleFromAction;
        const { actionGuid } = data.data.deleteRoleFromAction;
        const action2role = {
          guid: deletedGuid,
          roleGuid,
          actionGuid
        };
        context.commit('deleteRoleFromAction', action2role);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in deleteRoleFromAction apollo client => ${error}`, { root: true });
      });
  },

  setStatePermission(context, payload) {
    apolloClient.mutate({
      mutation: SET_STATE_PERMISSION,
      variables: {
        formGuid: context.state.formGuid,
        stateGuid: payload.stateGuid,
        roleGuid: payload.roleGuid,
        fieldGuid: payload.fieldGuid,
        read: payload.read,
        edit: payload.edit
      }
    })
      .then(data => {
        const { permissions } = data.data.setStatePermission;
        context.commit('setStatePermissions', permissions);
      })
      .catch(error => {
        context.commit('home/setShowErrorMsg',
          `Error in setStatePermission apollo client => ${error}`, { root: true });
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
