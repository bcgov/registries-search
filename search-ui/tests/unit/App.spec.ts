// External
import { mount } from '@vue/test-utils'
// Local
import App from '@/App.vue'
import { BcrsBreadcrumb } from '@/bcrs-common-components'
import { SbcHeader, SbcFooter } from '@/sbc-common-components'
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
  it('mounts App with expected child components', () => {
    expect(wrapper.findComponent(BcrsBreadcrumb).exists()).toBe(true)
    expect(wrapper.findComponent(SbcHeader).exists()).toBe(true)
    expect(wrapper.findComponent(SbcFooter).exists()).toBe(true)
  })
  it('registers jest running', () => {
    expect(wrapper.vm.isJestRunning).toBe(true)
  })
})
