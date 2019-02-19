const getters = {};

const actions = {
  getAllUsers({ commit }) {
    const users = ['Vasya', 'Perya', 'Ira'];
    commit('setProducts', users);
  }
};

const mutations = {
  setUsers(state, users) {
    state.all = users;
  }
};

const state = {
  all: ['Misha']
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
