// External
import { mount, VueWrapper } from '@vue/test-utils'
// Local
import { BusinessInfoView } from '@/views'
// import vuetify from '@/plugins/vuetify'
import store from '@/store'


describe('BusinessInfo tests', () => {
  let wrapper: VueWrapper<any>
  const identifier = 'CP1234567'

  beforeEach(async () => {
    wrapper = mount(BusinessInfoView, {
      // props: {
      //   identifier: identifier  // will be used in stubs for lear calls later
      // },
      global: {
        // plugins: [vuetify],
        provide: {
          store: store
        },
      },
      shallow: true  // stubs out children components
    })
  })
  it('renders BusinessInfo with expected child components', () => {
    // check headers are there
    expect(wrapper.html()).toContain('How to Access Business Documents')
    expect(wrapper.html()).toContain('Available Documents to Download:')
    // FUTURE: check fee summary / checkbox / filing history comp render
  })
})
