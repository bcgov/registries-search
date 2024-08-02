import { RegSearchResultI } from '../../src/interfaces/reg-search-i'

context('Search Business', () => {
  beforeEach(() => {
    cy.visitSearchPublic()
  })

  it('should display expected search bar', () => {
    // info text
    cy.get('[data-cy="search-input-info-text"]').should(
      'have.text',
      'Search for businesses registered or incorporated in B.C. and access their business documents.'
    )
    // search input
    cy.get('[data-cy="search-input"]').find('[data-cy="search-textfield"]').should('exist')
    // label text
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .should('have.attr', 'placeholder', 'Business Name or Incorporation/Registration Number or CRA Business Number')
    // hint text
    cy.get('[data-cy="search-input"]')
      .find('p')
      .should(
        'have.text',
        'Example: "Test Construction Inc.", "BC0000123", "987654321BC001"')
  })

  it('should display expected results after a search is triggered', () => {
    cy.get('[data-cy="search-results-table"]').should('not.exist')
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .type('test')
    cy.wait('@getBusinessSearchResults')
    cy.get('[data-cy="search-results-table"]').should('exist')
    cy.fixture('searchResultsBusiness.json').then((searchResponse) => {
      const results: RegSearchResultI[] = searchResponse.searchResults.results
      const totalResults = searchResponse.searchResults.totalResults
      // title
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.table-title')
        .should('include.text', `Search Results  (${totalResults} Businesses)`)
      // headers
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.base-table')
        .find('.base-table__header')
        .find('tr').eq(0).find('th').then((headerTitles) => {
          expect(headerTitles, '7 headers').to.have.length(7)
          expect(headerTitles.eq(0), 'Name header').to.have.text('Business Name')
          expect(headerTitles.eq(1), 'Identifier header').to.have.text('Incorporation/ Registration Number')
          expect(headerTitles.eq(2), 'BN header').to.have.text('CRA Business Number')
          expect(headerTitles.eq(3), 'Type header').to.have.text('Business Type')
          expect(headerTitles.eq(4), 'Status header').to.have.text('Status')
          expect(headerTitles.eq(5), 'Significant Individuals header').to.have.text('Significant Individuals')
          expect(headerTitles.eq(6), 'Actions header').to.have.text('Actions')
        })
      // filters
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.base-table')
        .find('.base-table__header')
        .find('tr').eq(1).find('th').then((headerFilters) => {
          expect(headerFilters, '7 filters').to.have.length(7)
        })
      // item data
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.base-table')
        .find('.base-table__body')
        .find('.base-table__body__row').as('rows')
      cy.get('@rows').should('have.length', results.length)
      for (const i in results) {
        cy.get('@rows').eq(Number(i)).find('.base-table__body__row__item').then((cols) => {
          expect(cols, '7 columns').to.have.length(7)
          expect(cols.eq(0), 'Name column - name').to.include.text(results[i].name.toUpperCase())
          expect(cols.eq(1), 'Identifier column').to.have.text(results[i].identifier)
          expect(cols.eq(2), 'BN column').to.have.text(results[i].bn || '')
          if (results[i].legalType === 'BEN') {
            expect(cols.eq(3), 'Type column').to.have.text('BC Benefit Company')
          } else if (results[i].legalType === 'CP') {
            expect(cols.eq(3), 'Type column').to.have.text('BC Cooperative Association')
          } else if (results[i].legalType === 'BEN') {
            expect(cols.eq(3), 'Type column').to.have.text('BC Benefit Company')
          } else if (results[i].legalType === 'SP') {
            expect(cols.eq(3), 'Type column').to.have.text('BC Sole Proprietorship')
          } else if (results[i].legalType === 'BC') {
            expect(cols.eq(3), 'Type column').to.have.text('BC Limited Company')
          }
          if (results[i].status === 'ACTIVE') {
            expect(cols.eq(4), 'Status column').to.have.text('Active')
          } else {
            expect(cols.eq(4), 'Status column').to.have.text('Historical')
          }
          expect(cols.eq(5), 'Significant Individuals column').to.have
            .text('Company indicated no significant individuals')
          if (['BEN', 'CP', 'SP', 'GP'].includes(results[i].legalType)) {
            expect(cols.eq(6), 'Actions column').to.have.text('Open')
          } else {
            expect(cols.eq(6), 'Actions column').to.have.text('')
          }
        })
      }
    })
  })
})
