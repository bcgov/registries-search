// External
import { mount } from '@vue/test-utils'
// Local
import App from '@/App.vue'
// import vuetify from '@/plugins/vuetify'
import store from '@/store'


// FUTURE: replace this with actual tests on App.vue
describe('App tests', () => {
  const wrapper = mount(App, {
    global: {
      // plugins: [vuetify],
      provide: {
        store: store
      },
    },
    shallow: true  // stubs out children components
  })
  it('runs', () => {
    expect(wrapper.vm.isJestRunning).toBe(true)
    expect(1).toBe(1)
  })
})
