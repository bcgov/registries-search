// External
import { createStore } from 'vuex'
// Local
import * as actions from './base-actions'
import * as getters from './base-getters'
import * as mutations from './base-mutations'
import { state } from './base-state'

export default createStore({
  state: { ...state },
  getters: { ...getters },
  mutations: { ...mutations },
  actions: { ...actions },
  modules: {},
  strict: process.env.NODE_ENV !== 'production',
})
