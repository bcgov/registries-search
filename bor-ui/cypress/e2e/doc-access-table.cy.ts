import { DocAccessTypeE } from '../../src/enums/doc-access-type-e'
import { DocAccessI } from '../../src/interfaces/doc-access-i'
import { apiToPacificDateTime } from '../../src/utils/date'

context('Document Access History Table', () => {
  beforeEach(() => {
    cy.visitSearchPublic()
  })

  it('should display tabs as expected', () => {
    cy.get('[data-cy="search-tabs"]').should('exist')
    cy.get('[data-cy="search-tabs"]').find('button[role=tab]').should('have.length', 2)
    // starts with search input visible
    cy.get('[data-cy="search-input"]').should('be.visible')
    cy.get('[data-cy="search-docAccess"]').should('not.be.visible')
    // click tab to document history
    cy.get('[data-cy="search-tabs"]').find('button[role=tab]').eq(1).click()
    cy.get('[data-cy="search-docAccess"]').should('exist')
  })

  it('should display document history table as expected', () => {
    cy.get('[data-cy="search-tabs"]').find('button[role=tab]').eq(1).click()
    cy.get('[data-cy="search-docAccess"]').should('be.visible')
    cy.get('[data-cy="search-docAccess-info"]').should(
      'have.text', 'This table will display up to 1000 of the most recent document activity in the last 14 days.')
    cy.fixture('purchases.json').then((purchasesResponse) => {
      const results: DocAccessI[] = purchasesResponse.documentAccessRequests
      const totalResults = results.length
      // title
      cy.get('[data-cy="search-docAccess-table"]')
        .find('.table-title')
        .should('include.text', `Documents (${totalResults})`)
      // headers
      cy.get('[data-cy="search-docAccess-table"]')
        .find('.base-table')
        .find('.base-table__header')
        .find('tr').eq(0).find('th').then((headerTitles) => {
          expect(headerTitles, '6 headers').to.have.length(6)
          expect(headerTitles.eq(0), 'Name header').to.have.text('Business Name')
          expect(headerTitles.eq(1), 'Identifier header').to.have.text('Number')
          expect(headerTitles.eq(2), 'Purchased Items header').to.have.text('Purchased Items')
          expect(headerTitles.eq(3), 'Date/Time header').to.have.text('Purchased Date/Time (pacific time)')
          expect(headerTitles.eq(4), 'User Name header').to.have.text('User Name')
          expect(headerTitles.eq(5), 'Actions header').to.have.text('Actions')
        })
      // filters
      cy.get('[data-cy="search-docAccess-table"]')
        .find('.base-table')
        .find('.base-table__header')
        .find('tr').eq(1).find('th').then((headerFilters) => {
          expect(headerFilters, '6 filters').to.have.length(6)
        })
      // item data
      cy.get('[data-cy="search-docAccess-table"]')
        .find('.base-table')
        .find('.base-table__body')
        .find('.base-table__body__row').as('rows')
      cy.get('@rows').should('have.length', results.length)
      for (const i in results) {
        cy.get('@rows').eq(Number(i)).find('.base-table__body__row__item').then((cols) => {
          expect(cols, '6 columns').to.have.length(6)
          expect(cols.eq(0), 'Name column - name').to.include.text(results[i].businessName?.toUpperCase())
          expect(cols.eq(1), 'Identifier column').to.have.text(results[i].businessIdentifier)
          for (const doc of results[i].documents) {
            if (doc.documentType === DocAccessTypeE.BUSINESS_SUMMARY_FILING_HISTORY) {
              expect(cols.eq(2), 'Purchased Items column').to.include.text('Business Summary')
            } else if (doc.documentType === DocAccessTypeE.CERTIFICATE_OF_GOOD_STANDING) {
              expect(cols.eq(2), 'Purchased Items column').to.include.text('Certificate of Good Standing')
            } else if (doc.documentType === DocAccessTypeE.CERTIFICATE_OF_STATUS) {
              expect(cols.eq(2), 'Purchased Items column').to.include.text('Certificate of Status')
            } else {
              expect(cols.eq(2), 'Purchased Items column').to.include.text('Letter Under Seal')
            }
          }
          expect(cols.eq(3), 'Date/Time column').to.have.text(apiToPacificDateTime(results[i].submissionDate))
          expect(cols.eq(4), 'User Name column').to.have.text(results[i].submitter)
          expect(cols.eq(5), 'Actions column').to.have.text('View Documents')
        })
      }
    })
  })
})
