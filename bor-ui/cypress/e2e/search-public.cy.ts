import { SearchResultI } from '../../src/interfaces/search-i'

context('Search public', () => {
  beforeEach(() => {
    cy.visitSearchPublic()
  })

  it('should display expected search bar', () => {
    // info text
    cy.get('[data-cy="search-input-info-text"]').should(
      'have.text',
      'Search for the names of people associated with businesses in B.C.'
    )
    // search input
    cy.get('[data-cy="search-input"]').find('[data-cy="search-textfield"]').should('exist')
    // label text
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .should('have.attr', 'placeholder', 'Person Name')
    // hint text
    cy.get('[data-cy="search-input"]')
      .find('p')
      .should(
        'have.text',
        'Example: "John Smith"')
  })

  it('should display expected results after a search is triggered', () => {
    cy.get('[data-cy="search-results-table"]').should('not.exist')
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .type('test')
    cy.wait('@getSearchResults')
    cy.get('[data-cy="search-results-table"]').should('exist')
    cy.fixture('searchResultsPublic.json').then((searchResponse) => {
      const results: SearchResultI[] = searchResponse.searchResults.results
      const totalResults = searchResponse.searchResults.totalResults
      // title
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.table-title')
        .should('include.text', `Search Results  (${totalResults} People)`)
      // headers
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.base-table')
        .find('.base-table__header')
        .find('tr').eq(0).find('th').then((headerTitles) => {
          expect(headerTitles, '4 headers').to.have.length(4)
          expect(headerTitles.eq(0), 'Name header').to.have.text('Name')
          expect(headerTitles.eq(1), 'Citizenship header').to.have.text('Citizenship')
          expect(headerTitles.eq(2), 'Business Details header').to.have.text('Business Details')
          expect(headerTitles.eq(3), 'Roles header').to.have.text('Roles')
        })
      // filters
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.base-table')
        .find('.base-table__header')
        .find('tr').eq(1).find('th').then((headerFilters) => {
          expect(headerFilters, '4 filters').to.have.length(4)
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
          // NB: business details and roles are combined into a single column
          expect(cols, '4 columns').to.have.length(3)
          // name
          expect(cols.eq(0), 'Name column - name').to.include.text(results[i].legalName.toUpperCase())
          expect(cols.eq(0), 'Name column - birthdate').to.include.text(results[i].birthDate || '')
          // citizenship
          expect(cols.eq(1), 'Citizenship column - no text').to.have.text('')
          if (results[i].nationalities) {
            expect(cols.eq(1).find('span'), 'Citizenship column - x flags')
              .to.have.length(results[i].nationalities.length)
            expect(cols.eq(1).find('span').attr('class'), 'Citizenship column - flag').includes('flag')
          } else {
            expect(cols.eq(1).find('span'), 'Citizenship column - no flag').to.have.length(0)
          }

          for (const roleIdx in results[i].roles) {
            const role = results[i].roles[roleIdx]
            const roleDivs = cols.eq(2).find('.inner-row-div').eq(Number(roleIdx)).find('.inner-col-div')
            // business
            expect(roleDivs.eq(0), 'Business Details column - identifier')
              .to.include.text(role.relatedIdentifier)
            expect(roleDivs.eq(0), 'Business Details column - name').to.include.text(role.relatedName)
            if (role.relatedBN) {
              expect(roleDivs.eq(0), 'Business Details column - bn').to.include.text(role.relatedBN)
            }

            // role
            expect(roleDivs.eq(1).text().toLowerCase(), 'Roles column').to.equal(role.roleType.toLowerCase())
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

    for (let i = 0; i < 4; i++) {
      cy.get('@headers').find('th').eq(Number(i)).invoke('outerWidth').then((headerWidth) => {
        if (i < 2) {
          cy.get('@firstRow').find('td').eq(Number(i)).invoke('outerWidth').then((bodyWidth) => {
            expect(headerWidth).to.equal(bodyWidth)
          })
        } else {
          cy.get('@firstRow').find('td').eq(2).find('.inner-row-div').eq(0).find('.inner-col-div').eq(Number(i) - 2)
            .invoke('outerWidth').then((bodyWidth) => {
              // NOTE: width of the screen cypress is running is smaller so it is off by more
              expect(headerWidth).to.be.closeTo(bodyWidth, 10)
            })
        }
      })
    }
  })
})
