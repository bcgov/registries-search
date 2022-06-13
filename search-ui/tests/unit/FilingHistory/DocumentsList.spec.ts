import { mount } from '@vue/test-utils'

// Components and sub-components
import DocumentsList from '@/components/FilingHistory/DocumentsList.vue'

describe('Documents List', () => {
    const SAMPLE_FILING = {
        availableOnPaperOnly: false,
        businessIdentifier: 'CP0001191',
        commentsCounts: 0,
        displayName: 'Annual Report (2019)',
        documentsLink: '',
        effectiveDate: '2019-12-13 00:00:00 GMT',
        filingId: 111,
        isFutureEffective: false,
        name: 'annualReport',
        status: 'COMPLETED',
        submittedDate: '2019-04-06 19:22:59.00 GMT',
        submitter: 'Cameron'
    }

    it('displays an empty documents list correctly', async () => {
        const filing = {
            ...SAMPLE_FILING,
            documents: []
        }

        const wrapper = mount(DocumentsList, { props: { filing } })
        //await Vue.nextTick()

        // verify the number of document buttons
        expect(wrapper.findAll('.download-one-btn').length).toBe(0)

        wrapper.unmount()
    })

    it('displays one document in the list correctly', async () => {
        const filing = {
            ...SAMPLE_FILING,
            documents: [
                { title: 'Document' }
            ]
        }

        const wrapper = mount(DocumentsList, { props: { filing } })
        //await Vue.nextTick()

        // verify the number of document buttons
        const documentBtns = wrapper.findAll('.download-one-btn')
        expect(documentBtns.length).toBe(1)

        // verify the individual document button
        expect(documentBtns[0].text()).toContain('Document')

        // verify that there is no Download All button
        expect(wrapper.find('.download-all-btn').exists()).toBe(false)

        wrapper.unmount()
    })

    it('displays multiple documents in the list correctly', async () => {
        const filing = {
            ...SAMPLE_FILING,
            documents: [
                { title: 'Document 1' },
                { title: 'Document 2' }
            ]
        }

        const wrapper = mount(DocumentsList, { props: { filing } })
        //await Vue.nextTick()

        // verify the number of document buttons
        const documentBtns = wrapper.findAll('.download-one-btn')
        expect(documentBtns.length).toBe(2)

        // verify the individual document buttons
        expect(documentBtns[0].text()).toContain('Document 1')
        expect(documentBtns[1].text()).toContain('Document 2')

        // verify the Download All button
        expect(wrapper.find('.download-all-btn').text()).toContain('Download All')

        wrapper.unmount()
    })

    it('sets the buttons active when documents are not loading or they are unlocked', async () => {
        const filing = {
            ...SAMPLE_FILING,
            documents: [
                { title: 'Document 1' },
                { title: 'Document 2' }
            ]
        }

        const wrapper = mount(DocumentsList, { props: { filing: filing, 
            loadingOne: false, loadingAll: false, isLocked: false } })

        const documentBtns = wrapper.findAll('.download-one-btn')

        // verify that all buttons are enabled and not loading
        expect(documentBtns[0].attributes('disabled')).toEqual("false")
        expect(documentBtns[1].attributes('disabled')).toEqual("false")
        expect(wrapper.find('.download-all-btn').attributes('disabled')).toEqual("false")
        wrapper.unmount()
    })

    it('sets the buttons disabled when documents are not paid for', async () => {
        const filing = {
            ...SAMPLE_FILING,
            documents: [
                { title: 'Document 1' },
                { title: 'Document 2' }
            ]
        }

        const wrapper = mount(DocumentsList, { props: { filing: filing, 
            loadingOne: false, loadingAll: false, isLocked: true } })

        const documentBtns = wrapper.findAll('.download-one-btn')

        // verify that all buttons are enabled and not loading
        expect(documentBtns[0].attributes('disabled')).toEqual("true")
        expect(documentBtns[1].attributes('disabled')).toEqual("true")
        expect(wrapper.find('.download-all-btn').attributes('disabled')).toEqual("true")
        wrapper.unmount()
    })

    it('sets the buttons disabled when one document is loading', async () => {
        const filing = {
            ...SAMPLE_FILING,
            documents: [
                { title: 'Document 1' },
                { title: 'Document 2' }
            ]
        }

        const wrapper = mount(DocumentsList, { props: { filing: filing, 
            loadingOne: true, loadingAll: false, isLocked: false } })

        const documentBtns = wrapper.findAll('.download-one-btn')

        // verify that all buttons are enabled and not loading
        expect(documentBtns[0].attributes('disabled')).toEqual("true")
        expect(documentBtns[1].attributes('disabled')).toEqual("true")
        expect(wrapper.find('.download-all-btn').attributes('disabled')).toEqual("true")
        wrapper.unmount()
    })

    it('sets the buttons disabled when one all documents are loading', async () => {
        const filing = {
            ...SAMPLE_FILING,
            documents: [
                { title: 'Document 1' },
                { title: 'Document 2' }
            ]
        }

        const wrapper = mount(DocumentsList, { props: { filing: filing,
             loadingOne: false, loadingAll: true, isLocked: false } })

        const documentBtns = wrapper.findAll('.download-one-btn')

        // verify that all buttons are enabled and not loading
        expect(documentBtns[0].attributes('disabled')).toEqual("true")
        expect(documentBtns[1].attributes('disabled')).toEqual("true")
        expect(wrapper.find('.download-all-btn').attributes('disabled')).toEqual("true")
        wrapper.unmount()
    })
})
