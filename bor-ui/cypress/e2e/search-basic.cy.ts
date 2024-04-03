context('Search basic', () => {
  beforeEach(() => {
    cy.visitSearch()
  })
  it('should display expected search bar', () => {
    // info text
    cy.get('[data-cy="search-input-info-text"]').should(
      'have.text',
      'Search for the names, addresses, and business email addresses of people associated with businesses in B.C.'
    )
    // search input
    cy.get('[data-cy="search-input"]').find('#search-bar-field').should('exist')
    // label text
    cy.get('[data-cy="search-input"]')
      .find('#search-bar-field')
      .siblings()
      .contains('Director Name, Address, and/or Email Address')
      .should('exist')
    // hint text
    cy.get('[data-cy="search-input"]')
      .find('.v-messages__message')
      .should('have.text', 'Example: "John Smith", "123 Main St", "V1V 1V1", "John Smith Victoria", "j.smith@123.aba"')
  })
  it('should display expected results after a search is triggered', () => {
    cy.get('[data-cy="search-results-table"]').should('not.exist')
    cy.get('[data-cy="search-input"]')
      .find('#search-bar-field')
      .type('test')
    cy.wait('@getSearchResults')
    cy.get('[data-cy="search-results-table"]').should('exist')
    cy.fixture('searchResultsBasic.json').then((searchResponse) => {
      const results = searchResponse.searchResults.results
      const totalResults = searchResponse.searchResults.totalResults
      // title
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.table-title')
        .should('include.text', `Search Results  (${totalResults} People)`)
        .should('include.text', 'Maximum results to export1000')
        .should('include.text', 'Export to .xlsx')
      // headers
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.base-table')
        .find('.base-table__header')
        .find('tr').eq(0).find('th').then((headerTitles) => {
          expect(headerTitles, '8 headers').to.have.length(8)
          expect(headerTitles.eq(0), 'Name header').to.have.text('Name')
          expect(headerTitles.eq(1), 'Address header').to.have.text('Address')
          expect(headerTitles.eq(2), 'Roles header').to.have.text('Roles')
          expect(headerTitles.eq(3), 'Effective Dates header').to.have.text('Effective Dates')
          expect(headerTitles.eq(4), 'Business Details header').to.have.text('Business Details')
          expect(headerTitles.eq(5), 'Business Status header').to.have.text('Business Status')
          expect(headerTitles.eq(6), 'Business Email header').to.have.text('Business Email')
          expect(headerTitles.eq(7), 'Actions header').to.have.text('')
        })
      // filters
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.base-table')
        .find('.base-table__header')
        .find('tr').eq(1).find('th').then((headerFilters) => {
          // TODO: fill these out
          expect(headerFilters, '8 filters').to.have.length(8)
        })
      // item data
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.base-table')
        .find('.base-table__body')
        .find('tr').as('rows')
      cy.get('@rows').should('have.length', results.length)
      for (const i in results) {
        cy.get('@rows').eq(Number(i)).find('td').then((cols) => {
          expect(cols, '8 columns').to.have.length(8)
          // name
          expect(cols.eq(0), 'Name column').to.have.text(results[i].legalName)
          // address
          const address = results[i].entityAddresses[0]
          expect(cols.eq(1), 'Address column - street').to.include.text(address.streetAddress)
          expect(cols.eq(1), 'Address column - city').to.include.text(address.addressCity)
          expect(cols.eq(1), 'Address column - region').to.include.text(address.addressRegion)
          expect(cols.eq(1), 'Address column - postal code').to.include.text(address.postalCode)
          expect(cols.eq(1), 'Address column - country').to.include.text(address.addressCountry)
          // role
          const role = results[i].roles[0]
          expect(cols.eq(2).text().toLowerCase(), 'Roles column').to.equal(role.roleType.toLowerCase())
          // dates
          const date = role.roleDates[0]
          if (role.roleType === 'INCORPORATOR') {
            expect(cols.eq(3), 'Effective Dates column - start').to.have.text(
              date.start ? date.start.substring(0, 10) : 'Unknown')
          } else {
            expect(cols.eq(3), 'Effective Dates column - start').to.include.text(
              date.start ? date.start.substring(0, 10) : 'Unknown')
            expect(cols.eq(3), 'Effective Dates column - end').to.include.text(
              date.end ? date.end.substring(0, 10) : 'Current')
          }
          // business
          expect(cols.eq(4), 'Business Details column - identifier').to.include.text(role.relatedIdentifier)
          expect(cols.eq(4), 'Business Details column - name').to.include.text(role.relatedName)
          if (role.relatedBN) {
            expect(cols.eq(4), 'Business Details column - bn').to.include.text(role.relatedBN)
          }
          // business status
          expect(cols.eq(5).text().toLowerCase(), 'Business Status column').to.equal(role.relatedState.toLowerCase())
          // business email
          expect(cols.eq(6), 'Business Email column').to.have.text(role.relatedEmail || '')
          // actions
          expect(cols.eq(7), 'Actions column').to.have.text('')
        })
      }
    })
  })
})
