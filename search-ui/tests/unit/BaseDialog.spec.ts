import { flushPromises, mount, VueWrapper } from '@vue/test-utils'
// local
import { BaseDialog } from '@/components'
import { DialogOptionsI } from '@/interfaces'

describe('BaseTable tests', () => {
  let wrapper: VueWrapper<any>

  let testVar = 0
  let testVarClose = 0

  const testOptions: DialogOptionsI = {
    buttons: [{
      onClick: (val: number) => testVar = val,
      onClickArgs: [2],
      onClickClose: false,
      text: 'Set to 2'
    }, {
      onClick: (val: number) => testVar = val,
      onClickArgs: [1],
      onClickClose: true,
      text: 'Set to 1 and close'
    }],
    onClose: (val: number) => testVarClose = val,
    onCloseArgs: [3],
    text: 'test text',
    title: 'test title'
  }

  beforeEach(async () => {
    wrapper = mount(BaseDialog, {
      props: {
        display: true,
        options: testOptions
      }
    })
  })
  it('renders BaseDialog', async () => {
    // test everything renders
    expect(wrapper.find('.base-dialog').exists()).toBe(true)
    expect(wrapper.find('.base-dialog__title').exists()).toBe(true)
    expect(wrapper.find('.base-dialog__text').exists()).toBe(true)
    expect(wrapper.find('.base-dialog__btn-container').exists()).toBe(true)
    expect(wrapper.find('.base-dialog__btn').exists()).toBe(true)
  })

  it('sets given options', async () => {
    expect(wrapper.find('.base-dialog__title').text()).toContain(testOptions.title)
    expect(wrapper.find('.base-dialog__text').text()).toContain(testOptions.text)
    expect(wrapper.findAll('.base-dialog__btn').length).toBe(2)
    expect(wrapper.findAll('.base-dialog__btn')[0].text()).toContain(testOptions.buttons[0].text)
    expect(wrapper.findAll('.base-dialog__btn')[1].text()).toContain(testOptions.buttons[1].text)
  })

  it('given buttons work as expected', async () => {
    // 1st btn
    expect(testVar).toBe(0)
    wrapper.findAll('.base-dialog__btn')[0].trigger('click')
    await flushPromises()
    expect(testVar).toBe(2)
    expect(wrapper.emitted().close).toBeUndefined()
    // 2nd btn
    expect(testVar).toBe(2)
    wrapper.findAll('.base-dialog__btn')[1].trigger('click')
    expect(testVar).toBe(1)
    expect(wrapper.emitted().close.length).toBe(1)
  })

  it('close button works as expected', async () => {
    expect(testVarClose).toBe(0)
    expect(wrapper.emitted().close).toBeUndefined()
    wrapper.find('.base-dialog__close-btn').trigger('click')
    await flushPromises()
    expect(testVarClose).toBe(3)
    expect(wrapper.emitted().close.length).toBe(1)
  })
})