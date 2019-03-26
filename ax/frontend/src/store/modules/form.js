const mutations = {
  increment(state) {
    state.count += 1;
    return state;
  }
};

const getters = {};
const actions = {};

const state = {
  guid: null,
  name: null,
  dbName: null,
  icon: null,
  tomLabel: null,
  fields: []
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
