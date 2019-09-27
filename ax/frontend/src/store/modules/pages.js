const getDefaultState = () => {
  return {}
}

const mutations = {
  resetState(state) {
    Object.assign(state, getDefaultState())
  },
};

const getters = {};
const actions = {};

const state = getDefaultState();

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
