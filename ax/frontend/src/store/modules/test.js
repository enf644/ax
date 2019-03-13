const mutations = {
  increment(state) {
    state.count += 1;
    return state;
  },
  decrement(state) {
    state.count -= 1;
    return state;
  }
};

const getters = {};
const actions = {};

const state = {
  count: 0
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
