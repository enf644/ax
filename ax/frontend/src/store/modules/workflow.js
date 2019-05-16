const mutations = {
  setWorkflowData(state, data) {
    if (data) {
      state.formGuid = data.guid;
      state.formDbName = data.dbName;
      state.roles = data.roles ? data.roles.edges.map(edge => edge.node) : null;
      state.states = data.states ? data.states.edges.map(edge => edge.node) : null;
      state.actions = data.actions ? data.actions.edges.map(edge => edge.node) : null;
    } else {
      state.formGuid = null;
      state.formDbName = null;
      state.roles = [];
      state.states = [];
      state.actions = [];
    }
  }
};

const getters = {};
const actions = {};

const state = {
  formGuid: null,
  formDbName: null,
  roles: [],
  states: [],
  actions: []
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
