import { mount } from '@vue/test-utils'

// Components and sub-components
import FilingHistoryList from '@/components/FilingHistory/FilingHistory.vue'
import CompletedAlteration from '@/components/FilingHistory/CompletedAlteration.vue'
import FutureEffective from '@/components/FilingHistory/FutureEffective.vue'
import FutureEffectivePending from '@/components/FilingHistory/FutureEffectivePending.vue'
import PaperFiling from '@/components/FilingHistory/PaperFiling.vue'
import PendingFiling from '@/components/FilingHistory/PendingFiling.vue'
import StaffFiling from '@/components/FilingHistory/StaffFiling.vue'
import { DetailsList } from '@/components/common'
import { useEntity, useFilingHistory } from '@/composables'
import { EntityI } from '@/interfaces/entity'
import { BusinessStatuses, BusinessTypes, FilingStatus, FilingTypes } from '@/enums'

const { setEntity } = useEntity()
const { filingHistory } = useFilingHistory()

const cp_entity: EntityI = {
    identifier: 'CP0001191',
    legalType: BusinessTypes.COOPERATIVE_ASSOCIATION,
    name: 'Test CP',
    status: BusinessStatuses.ACTIVE,
    goodStanding: true
}

// Boilerplate to prevent the complaint "[Vuetify] Unable to locate target [data-app]"
const app: HTMLDivElement = document.createElement('div')
app.setAttribute('data-app', 'true')
document.body.append(app)

describe('Filing History List - misc functionality', () => {
    const SAMPLE_FILINGS = [
        {
            availableOnPaperOnly: false,
            businessIdentifier: 'CP0001191',
            commentsCount: 0,
            displayName: 'Annual Report',
            effectiveDate: '2019-06-02 19:22:59 GMT',
            filingId: 111,
            isFutureEffective: false,
            name: FilingTypes.ANNUAL_REPORT,
            status: FilingStatus.COMPLETED,
            submittedDate: '2019-06-02 19:22:59 GMT',
            submitter: 'Submitter 1',
            documentsLink: '',
            commentsLink: '',
            filingLink: '',
            data: {
                applicationDate: '',
                legalFilings: ['annualReport']
            }
        },
        {
            availableOnPaperOnly: false,
            businessIdentifier: 'CP0001191',
            commentsCount: 2,
            displayName: 'Change of Address',
            // Effective Date is way in the future so it's always > now
            effectiveDate: '2099-12-13 08:00:00 GMT', // Dec 13, 2099 at 00:00:00 am Pacific
            filingId: 222,
            isFutureEffective: true,
            name: FilingTypes.CHANGE_OF_ADDRESS,
            status: FilingStatus.PAID,
            submittedDate: '2019-12-12 19:22:59 GMT', // Dec 12, 2019 at 11:22:59 am Pacific
            submitter: 'Submitter 2',
            documentsLink: '',
            commentsLink: '',
            filingLink: '',
            data: {
                applicationDate: '',
                legalFilings: ['changeOfAddress']
            }
        }
    ]

    it('handles empty data', async () => {


        setEntity(cp_entity)
        filingHistory.filings = []

        const wrapper = mount(FilingHistoryList, { isLocked: true })
        const vm = wrapper.vm as any


        expect(vm.historyItems.length).toEqual(0)
        expect(wrapper.findAll('.filing-history-item').length).toEqual(0)
        expect(wrapper.find('.no-results').text()).toContain('No filing history')

        wrapper.unmount()
    })

    it('shows multiple filings"', async () => {
        // init store        
        setEntity(cp_entity)
        filingHistory.filings = []

        const wrapper = mount(FilingHistoryList, { isLocked: true })
        filingHistory.filings = SAMPLE_FILINGS

        const vm = wrapper.vm as any
        expect(vm.filings.length).toEqual(2)
        await vm.loadData()
        expect(vm.historyItems.length).toEqual(2)
        await wrapper.vm.$nextTick()

        expect(wrapper.findAll('.filing-history-item')[0].find('.item-header__title').text())
        .toEqual("Annual Report")
        expect(wrapper.findAll('.filing-history-item')[0].find('.item-header__subtitle').text())
        .toContain("FILED AND PAID  (Filed on  June 2, 2019 at 12:22 pm Pacific time) EFFECTIVE"+
         " as of  June 2, 2019 at 12:22 pm Pacific time")
        expect(wrapper.findAll('.filing-history-item')[1].find('.item-header__title').text())
        .toEqual("Change of Address")

        wrapper.unmount()
    })

    it('expands a paper-only filing', async () => {
        // init store
        setEntity(cp_entity)
        filingHistory.filings = [
            {
                availableOnPaperOnly: true,
                businessIdentifier: 'CP0001191',
                commentsCount: 0,
                displayName: 'Change of Directors',
                effectiveDate: '2019-11-20 22:17:54 GMT',
                filingId: 222,
                isFutureEffective: false,
                name: FilingTypes.CHANGE_OF_DIRECTORS,
                status: FilingStatus.COMPLETED,
                submittedDate: '2019-03-09',
                submitter: 'Cameron',
                documentsLink: '',
                commentsLink: '',
                filingLink: '',
                data: {
                    applicationDate: '',
                    legalFilings: ['changeOfDirectors']
                }
            }
        ]

        const wrapper = mount(FilingHistoryList, { isLocked: true })
        const vm = wrapper.vm as any

        vm.loadData()
        await vm.$nextTick()

        // verify Request a Copy button
        const button = wrapper.find('.expand-btn')
        expect(button.text()).toContain('Request a Copy')

        // expand details
        button.trigger('click')
        await vm.$nextTick()


        // verify Close button
        expect(wrapper.find('.expand-btn').text()).toContain('Close')

        // verify details
        expect(vm.panel).toBe(0) // first row is expanded
        expect(wrapper.findComponent(CompletedAlteration).exists()).toBe(false)
        expect(wrapper.findComponent(FutureEffective).exists()).toBe(false)
        expect(wrapper.findComponent(FutureEffectivePending).exists()).toBe(false)
        expect(wrapper.findComponent(PaperFiling).exists()).toBe(true)
        expect(wrapper.findComponent(PendingFiling).exists()).toBe(false)
        expect(wrapper.findComponent(StaffFiling).exists()).toBe(false)
        expect(wrapper.findComponent(DetailsList).exists()).toBe(false)

        wrapper.unmount()
    })

    it('expands a regular filing', async () => {
        // init store
        setEntity(cp_entity)
        filingHistory.filings = [
            {
                availableOnPaperOnly: false,
                businessIdentifier: 'CP0001191',
                commentsCount: 0,
                displayName: 'Annual Report',
                effectiveDate: '2019-11-20 22:17:54 GMT',
                filingId: 111,
                isFutureEffective: false,
                name: FilingTypes.ANNUAL_REPORT,
                status: FilingStatus.COMPLETED,
                submittedDate: '2019-06-02',
                submitter: 'Cameron',
                documentsLink: 'http://test',
                commentsLink: '',
                filingLink: '',
                data: {
                    applicationDate: '',
                    legalFilings: ['annualReport']
                }
            }
        ]

        const wrapper = mount(FilingHistoryList, { isLocked: true })
        const vm = wrapper.vm as any
        jest.spyOn(vm, 'loadDocuments').mockImplementation(() => (
            Promise.resolve([])
        ))
        vm.loadData()
        await vm.$nextTick()
        // verify View Documents button
        const button = wrapper.find('.expand-btn')
        expect(button.text()).toContain('View Documents')

        expect(wrapper.findComponent(CompletedAlteration).exists()).toBe(false)
        expect(wrapper.findComponent(FutureEffective).exists()).toBe(false)
        expect(wrapper.findComponent(FutureEffectivePending).exists()).toBe(false)
        expect(wrapper.findComponent(PaperFiling).exists()).toBe(false)
        expect(wrapper.findComponent(PendingFiling).exists()).toBe(false)
        expect(wrapper.findComponent(StaffFiling).exists()).toBe(false)
        expect(wrapper.findComponent(DetailsList).exists()).toBe(false)

        wrapper.unmount()
    })
})
