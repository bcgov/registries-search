import { SearchResultRoleI } from '../../src/interfaces/search-i'

context('Search limited', () => {
  beforeEach(() => {
    cy.visitSearchLimited()
  })
  it('should display expected search bar', () => {
    // info text
    cy.get('[data-cy="search-input-info-text"]').should(
      'have.text',
      'Search for the names, addresses, and business email addresses of people associated with businesses in B.C.'
    )
    // search input
    cy.get('[data-cy="search-input"]').find('[data-cy="search-textfield"]').should('exist')
    // label text
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .should('have.attr', 'placeholder', 'Person Name, Address, and/or Business Email Address')
    // hint text
    cy.get('[data-cy="search-input"]')
      .find('p')
      .should('have.text', 'Example: "John Smith", "123 Main St", "V1V 1V1", "John Smith Victoria", "j.smith@123.aba"')
  })
  it('should display expected results after a search is triggered', () => {
    cy.get('[data-cy="search-results-table"]').should('not.exist')
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .type('test')
    cy.wait('@getSearchResults')
    cy.get('[data-cy="search-results-table"]').should('exist')
    cy.fixture('searchResultsLimited.json').then((searchResponse) => {
      const results = searchResponse.searchResults.results
      const totalResults = searchResponse.searchResults.totalResults
      // title
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.table-title')
        .should('include.text', `Search Results  (${totalResults} People)`)
        .should('include.text', '1000')
        .should('include.text', 'Export to .xlsx')
      // headers
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.base-table')
        .find('.base-table__header')
        .find('tr').eq(0).find('th').then((headerTitles) => {
          expect(headerTitles, '7 headers').to.have.length(7)
          expect(headerTitles.eq(0), 'Name header').to.have.text('Name')
          expect(headerTitles.eq(1), 'Address header').to.have.text('Address')
          expect(headerTitles.eq(2), 'Roles header').to.have.text('Roles')
          expect(headerTitles.eq(3), 'Effective Dates header').to.have.text('Effective Dates')
          expect(headerTitles.eq(4), 'Business Details header').to.have.text('Business Details')
          expect(headerTitles.eq(5), 'Business Status header').to.have.text('Business Status')
          expect(headerTitles.eq(6), 'Business Email header').to.have.text('Business Email')
        })
      // filters
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.base-table')
        .find('.base-table__header')
        .find('tr').eq(1).find('th').then((headerFilters) => {
          // TODO: fill these out
          expect(headerFilters, '7 filters').to.have.length(7)
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
          // NB: roles, effective dates, business details, status, email are combined into a single column
          expect(cols, '3 columns').to.have.length(3)
          // name
          expect(cols.eq(0), 'Name column').to.have.text(results[i].legalName)
          // address
          const address = results[i].entityAddresses[0]
          expect(cols.eq(1), 'Address column - street').to.include.text(address.streetAddress)
          expect(cols.eq(1), 'Address column - city').to.include.text(address.addressCity)
          expect(cols.eq(1), 'Address column - region').to.include.text(address.addressRegion)
          expect(cols.eq(1), 'Address column - postal code').to.include.text(address.postalCode)
          expect(cols.eq(1), 'Address column - country').to.include.text(address.addressCountry)
          // role column spans across all role data columns
          for (const roleIdx in results[i].roles) {
            const role: SearchResultRoleI = results[i].roles[roleIdx]
            const roleDivs = cols.eq(2).find('.inner-row-div').eq(Number(roleIdx)).find('.inner-col-div')
            // role
            expect(roleDivs.eq(0).text().toLowerCase(), 'Roles column').to.equal(role.roleType.toLowerCase())
            // dates
            for (const date of role.roleDates) {
              if (role.roleType === 'INCORPORATOR') {
                expect(roleDivs.eq(1), 'Effective Dates column - incorp').to.have.text(
                  date.start ? date.start.substring(0, 10) : 'Unknown')
              } else {
                expect(roleDivs.eq(1), 'Effective Dates column - start').to.include.text(
                  date.start ? date.start.substring(0, 10) : 'Unknown')
                expect(roleDivs.eq(1), 'Effective Dates column - end').to.include.text(
                  date.end ? date.end.substring(0, 10) : 'Current')
              }
            }
            // business details
            expect(roleDivs.eq(2), 'Business Details column - identifier')
              .to.include.text(role.relatedIdentifier)
            expect(roleDivs.eq(2), 'Business Details column - name').to.include.text(role.relatedName)
            if (role.relatedBN) {
              expect(roleDivs.eq(2), 'Business Details column - bn').to.include.text(role.relatedBN)
            }
            // business status
            expect(roleDivs.eq(3).text().toLowerCase(), 'Business Status column')
              .to.equal(role.relatedState.toLowerCase())
            // business email
            expect(roleDivs.eq(4).text().toLowerCase(), 'Business Email column')
              .to.equal((role.relatedEmail || '').toLowerCase())
          }
        })
      }
    })
  })

  it('table columns should have the same width as their headers', () => {
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .type('test')
    cy.wait('@getSearchResults')

    cy.get('.base-table__header').find('tr').first().as('headers')
    cy.get('.base-table__body').find('tr').first().as('firstRow')

    for (let i = 0; i < 7; i++) {
      cy.get('@headers').find('th').eq(Number(i)).invoke('outerWidth').then((headerWidth) => {
        if (i < 2) {
          cy.get('@firstRow').find('td').eq(Number(i)).invoke('outerWidth').then((bodyWidth) => {
            expect(headerWidth).to.equal(bodyWidth)
          })
        } else if (i === 7) {
          cy.get('@firstRow').find('td').eq(3).invoke('outerWidth').then((bodyWidth) => {
            expect(headerWidth).to.equal(bodyWidth)
          })
        } else {
          cy.get('@firstRow').find('td').eq(2).find('.inner-row-div').eq(0).find('.inner-col-div').eq(Number(i) - 2)
            .invoke('outerWidth').then((bodyWidth) => {
              // NOTE: width of the screen cypress is running is smaller so it is off by more
              expect(headerWidth).to.be.closeTo(bodyWidth, 5)
            })
        }
      })
    }
  })
})
