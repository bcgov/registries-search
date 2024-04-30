import { SearchResultI } from '../../src/interfaces/search-i'
import { PersonControlTypeE } from '../../src/enums/person-control-type-e'

context('Search extended', () => {
  beforeEach(() => {
    cy.visitSearchExtended()
  })
  it('should display expected search bar', () => {
    // info text
    cy.get('[data-cy="search-input-info-text"]').should(
      'have.text',
      'Search for the names, addresses, SIN/TTN/ITN, and ' +
      'email addresses of people associated with businesses in B.C.'
    )
    // search input
    cy.get('[data-cy="search-input"]').find('#search-bar-field').should('exist')
    // label text
    cy.get('[data-cy="search-input"]')
      .find('#search-bar-field')
      .siblings()
      .contains('Person Name, Address, SIN/TTN/ITN, and/or Email Address')
      .should('exist')
    // hint text
    cy.get('[data-cy="search-input"]')
      .find('.v-messages__message')
      .should(
        'have.text',
        'Example: "John Smith", "123 Main St", "V1V 1V1", "John Smith Victoria", "j.smith@123.aba", "000 000 000"')
  })
  it('should display expected results after a search is triggered', () => {
    cy.get('[data-cy="search-results-table"]').should('not.exist')
    cy.get('[data-cy="search-input"]')
      .find('#search-bar-field')
      .type('test')
    cy.wait('@getSearchResults')
    cy.get('[data-cy="search-results-table"]').should('exist')
    cy.fixture('searchResultsExtended.json').then((searchResponse) => {
      const results: SearchResultI[] = searchResponse.searchResults.results
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
          expect(headerTitles, '7 headers').to.have.length(7)
          expect(headerTitles.eq(0), 'Name header').to.have.text('Name')
          expect(headerTitles.eq(1), 'Information header').to.have.text('Information')
          expect(headerTitles.eq(2), 'Citizenship header').to.have.text('Citizenship')
          expect(headerTitles.eq(3), 'Roles header').to.have.text('Roles')
          expect(headerTitles.eq(4), 'Business Details header').to.have.text('Business Details')
          expect(headerTitles.eq(5), 'Details header').to.have.text('Details')
          expect(headerTitles.eq(6), 'Effective Dates header').to.have.text('Effective Dates')
          // NB: will be added back in later
          // expect(headerTitles.eq(7), 'Actions header').to.have.text('Actions')
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
          // NB: roles, business details, control and effective dates are combined into a single column
          expect(cols, '4 columns').to.have.length(4)
          // name
          expect(cols.eq(0), 'Name column - name').to.include.text(results[i].legalName.toUpperCase())
          expect(cols.eq(0), 'Name column - preferred name').to.include.text(results[i].alternateName || '')
          expect(cols.eq(0), 'Name column - birthdate').to.include.text(results[i].birthDate || '')
          // information
          expect(cols.eq(1), 'Information column - tax number').to.include.text(results[i].taxNumber || '')
          expect(cols.eq(1), 'Information column - email').to.include.text(results[i].email || '')
          const address = results[i].entityAddresses[0]
          expect(cols.eq(1), 'Information column - street').to.include.text(address.streetAddress)
          expect(cols.eq(1), 'Information column - city').to.include.text(address.addressCity)
          expect(cols.eq(1), 'Information column - region').to.include.text(address.addressRegion)
          expect(cols.eq(1), 'Information column - postal code').to.include.text(address.postalCode)
          expect(cols.eq(1), 'Information column - country').to.include.text(address.addressCountry)
          if (results[i].taxResidencies && results[i].taxResidencies.includes('CA')) {
            expect(cols.eq(1), 'Information column - tax residency').to.include.text('Tax ResidencyCanada')
          } else if (results[i].taxResidencies) {
            expect(cols.eq(1), 'Information column - tax residency').to.include.text('Tax ResidencyOther')
          }
          // citizenship
          expect(cols.eq(2), 'Citizenship column - no text').to.have.text('')
          if (results[i].nationalities) {
            expect(cols.eq(2).find('span'), 'Citizenship column - x flags')
              .to.have.length(results[i].nationalities.length)
            expect(cols.eq(2).find('span').attr('class'), 'Citizenship column - flag').includes('flag')
          } else {
            expect(cols.eq(2).find('span'), 'Citizenship column - no flag').to.have.length(0)
          }
          // role
          const role = results[i].roles[0]
          expect(cols.eq(3).find('td').eq(0).text().toLowerCase(), 'Roles column').to.equal(role.roleType.toLowerCase())
          // business
          expect(cols.eq(3).find('td').eq(1), 'Business Details column - identifier')
            .to.include.text(role.relatedIdentifier)
          expect(cols.eq(3).find('td').eq(1), 'Business Details column - name').to.include.text(role.relatedName)
          if (role.relatedBN) {
            expect(cols.eq(3).find('td').eq(1), 'Business Details column - bn').to.include.text(role.relatedBN)
          }
          // details
          if (role.relatedInterests) {
            role.relatedInterests.forEach((interest, index) => {
              switch (interest.details) {
                case PersonControlTypeE.DirectorsDirectControl:
                  expect(cols.eq(3).find('td').eq(2).find('.detail-icons-container').find('.detail-icon').find('img')
                    .eq(index).attr('alt')).includes('Direct control')
                  break
                case PersonControlTypeE.DirectorsInConcertControl:
                  expect(cols.eq(3).find('td').eq(2).find('.detail-icons-container').find('.detail-icon').find('img')
                    .eq(index).attr('alt'))
                    .includes('majority of directors through rights and/or exercised in concert')
                  break
                case PersonControlTypeE.DirectorsIndirectControl:
                  expect(cols.eq(3).find('td').eq(2).find('.detail-icons-container').find('.detail-icon').find('img')
                    .eq(index).attr('alt')).includes('Indirect control (through another business)')
                  break
                case PersonControlTypeE.DirectorsSignificantInfluence:
                  expect(cols.eq(3).find('td').eq(2).find('.detail-icons-container').find('.detail-icon').find('img')
                    .eq(index).attr('alt')).includes('Significant influence control')
                  break
                case PersonControlTypeE.SharesOrVotesBeneficialOwner:
                  expect(cols.eq(3).find('td').eq(2).find('.detail-icons-container').find('.detail-icon').find('img')
                    .eq(index).attr('alt')).includes('Beneficial owner (e.g., through a trust)')
                  break
                case PersonControlTypeE.SharesOrVotesInConcertControl:
                  expect(cols.eq(3).find('td').eq(2).find('.detail-icons-container').find('.detail-icon').find('img')
                    .eq(index).attr('alt'))
                    .includes('Indirect control (e.g., through another business)')
                  break
                case PersonControlTypeE.SharesOrVotesRegisteredOwner:
                  expect(cols.eq(3).find('td').eq(2).find('.detail-icons-container').find('.detail-icon').find('img')
                    .eq(index).attr('alt')).to.include('Registered owner')
                  break
                default:
                  expect(cols.eq(3).find('td').eq(2).find('.detail-icons-container').find('.detail-icon').find('img')
                    .eq(index).attr('alt'))
                    .includes('Any other reason(s) this individual is a significant individual')
              }
              if (interest.interestType === 'shareholding') {
                expect(cols.eq(3).find('td').eq(2), 'Details column - shares').to.include.text('Shares')
              } else if (interest.interestType === 'votingRights') {
                expect(cols.eq(3).find('td').eq(2), 'Details column - votes').to.include.text('Votes')
              }
            })
          } else {
            expect(cols.eq(3).find('td').eq(2), 'Details column').to.have.text('')
          }
          // dates
          const date = role.roleDates[0]
          if (role.roleType === 'INCORPORATOR') {
            expect(cols.eq(3).find('td').eq(3), 'Effective Dates column - start').to.have.text(
              date.start ? date.start.substring(0, 10) : 'Unknown')
          } else {
            expect(cols.eq(3).find('td').eq(3), 'Effective Dates column - start').to.include.text(
              date.start ? date.start.substring(0, 10) : 'Unknown')
            expect(cols.eq(3).find('td').eq(3), 'Effective Dates column - end').to.include.text(
              date.end ? date.end.substring(0, 10) : 'Current')
          }
          // actions - will be added back in later
          // expect(cols.eq(7).find('button'), 'Actions column - 1 button').to.have.length(1)
          // expect(cols.eq(7).find('button'), 'Actions column - text').to.include.text('Open')
        })
      }
    })
  })
})
