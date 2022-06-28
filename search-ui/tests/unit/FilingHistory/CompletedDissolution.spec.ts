import { mount } from '@vue/test-utils'
import CompletedDissolution from '@/components/FilingHistory/CompletedDissolution.vue'
import { useEntity } from '@/composables'
import { EntityI } from '@/interfaces/entity';
import { BusinessStatuses, BusinessTypes } from '@/enums';

const { setEntity } = useEntity();
const bc_entity: EntityI = {
    identifier: 'BC1234567',
    legalType: BusinessTypes.BENEFIT_COMPANY,
    name: 'MY COMPANY',
    status: BusinessStatuses.ACTIVE,
    goodStanding: true
}

const cp_entity: EntityI = {
    identifier: 'CP1234567',
    legalType: BusinessTypes.COOPERATIVE_ASSOCIATION,
    name: 'MY COMPANY',
    status: BusinessStatuses.ACTIVE,
    goodStanding: true
}


describe('Dissolution Filing', () => {
    it('Displays expected content with a null filing', () => {
        const wrapper = mount(CompletedDissolution, {
            props: { filing: null }
        })

        // verify content
        // verify content
        expect(wrapper.find('h4').exists()).toBe(false)
        expect(wrapper.findAll('p').length).toBe(0)
        wrapper.unmount()
    })

    it('Displays expected content with a valid Coop filing', () => {
        setEntity(cp_entity)
        const wrapper = mount(CompletedDissolution, {
            props: {
                filing: {
                    effectiveDate: new Date('2021-01-01 08:00:00 GMT')
                }
            }
        })

        // verify content
        expect(wrapper.find('h4').text()).toBe('Dissolution Complete')
        const paragraphs = wrapper.findAll('p')
        expect(paragraphs.length).toBe(2)
        expect(paragraphs[0].text()).toContain('The Cooperative Association MY COMPANY was successfully')
        expect(paragraphs[0].text()).toContain('dissolved on January 1, 2021 at 12:00 am Pacific time')
        expect(paragraphs[0].text()).toContain('The Cooperative Association has been struck')
        expect(paragraphs[0].text()).toContain('and ceased to be an incorporated Cooperative Association')
        expect(paragraphs[0].text()).toContain('under the Cooperative Association Act.')
        expect(paragraphs[1].text()).toContain('You are required to retain a copy of all')

        wrapper.unmount()
    })

    it('Displays expected content with a valid corp filing', () => {
        setEntity(bc_entity)
        const wrapper = mount(CompletedDissolution, {
            props: {
                filing: {
                    effectiveDate: new Date('2021-01-01 08:00:00 GMT')
                }
            }
        })

        // verify content
        expect(wrapper.find('h4').text()).toBe('Dissolution Complete')
        const paragraphs = wrapper.findAll('p')
        expect(paragraphs.length).toBe(2)
        expect(paragraphs[0].text()).toContain('The Company MY COMPANY was successfully')
        expect(paragraphs[0].text()).toContain('dissolved on January 1, 2021 at 12:00 am Pacific time')
        expect(paragraphs[0].text()).toContain('The Company has been struck')
        expect(paragraphs[0].text()).toContain('and ceased to be an incorporated Company')
        expect(paragraphs[0].text()).toContain('under the Business Corporations Act.')
        expect(paragraphs[1].text()).toContain('You are required to retain a copy of all')

        wrapper.unmount()
    })
})
