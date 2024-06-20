import { SearchResultI } from '../../src/interfaces/search-i'
import { PersonControlTypeE } from '../../src/enums/person-control-type-e'

context('Search extended', () => {
  beforeEach(() => {
    cy.visitSearchExtended()
    cy.get('[data-cy="search-radios"]').find('label').eq(1).click()
  })

  it('should display expected search bar', () => {
    // info text
    cy.get('[data-cy="search-input-info-text"]').should(
      'have.text',
      'Search for the names, addresses, SIN/TTN/ITN, and ' +
      'email addresses of people associated with businesses in B.C.'
    )
    // search input
    cy.get('[data-cy="search-input"]').find('[data-cy="search-textfield"]').should('exist')
    // label text
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .should('have.attr', 'placeholder', 'Person Name, Address, SIN/TTN/ITN, and/or Email Address')
    // hint text
    cy.get('[data-cy="search-input"]')
      .find('p')
      .should(
        'have.text',
        'Example: "John Smith", "123 Main St", "V1V 1V1", "John Smith Victoria", "j.smith@123.aba", "000 000 000"')
  })

  it('should display expected results after a search is triggered', () => {
    cy.get('[data-cy="search-results-table"]').should('not.exist')
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
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
          expect(headerTitles.eq(1), 'Information header').to.have.text('Information')
          expect(headerTitles.eq(2), 'Citizenship header').to.have.text('Citizenship')
          expect(headerTitles.eq(3), 'Business Details header').to.have.text('Business Details')
          expect(headerTitles.eq(4), 'Roles header').to.have.text('Roles')
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
          expect(cols.eq(1), 'Information column - phone').to.include.text(results[i].phoneNumber || '')
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

          for (const roleIdx in results[i].roles) {
            const role = results[i].roles[roleIdx]
            const roleDivs = cols.eq(3).find('.inner-row-div').eq(Number(roleIdx)).find('.inner-col-div')

            // business
            expect(roleDivs.eq(0), 'Business Details column - identifier')
              .to.include.text(role.relatedIdentifier)
            expect(roleDivs.eq(0), 'Business Details column - name').to.include.text(role.relatedName)
            if (role.relatedBN) {
              expect(roleDivs.eq(0), 'Business Details column - bn').to.include.text(role.relatedBN)
            }
            if (role.relatedAddresses) {
              expect(roleDivs.eq(0).find('[data-cy=address-display]'), 'Business Details column - city')
                .to.include.text(role.relatedAddresses[0].addressCity || '')
              expect(roleDivs.eq(0).find('[data-cy=address-display]'), 'Business Details column - country')
                .to.include.text(role.relatedAddresses[0].addressCountry || '')
              expect(roleDivs.eq(0).find('[data-cy=address-display]'), 'Business Details column - region')
                .to.include.text(role.relatedAddresses[0].addressRegion || '')
              expect(roleDivs.eq(0).find('[data-cy=address-display]'), 'Business Details column - postal code')
                .to.include.text(role.relatedAddresses[0].postalCode || '')
              expect(roleDivs.eq(0).find('[data-cy=address-display]'), 'Business Details column - street')
                .to.include.text(role.relatedAddresses[0].streetAddress || '')
              expect(roleDivs.eq(0).find('[data-cy=address-display]'), 'Business Details column - street additional')
                .to.include.text(role.relatedAddresses[0].streetAdditional || '')
              if (role.relatedAddresses[0].locationDescription) {
                expect(roleDivs.eq(0)
                  .find('[data-cy=address-display]'), 'Business Details column - Location Description (title)')
                  .to.include.text('Location Description')
                expect(roleDivs.eq(0)
                  .find('[data-cy=address-display]'), 'Business Details column - Location Description (content)')
                  .to.include.text(role.relatedAddresses[0].locationDescription)
              }
            }

            // role
            expect(roleDivs.eq(1).text().toLowerCase(), 'Roles column').to.equal(role.roleType.toLowerCase())

            // details
            if (role.relatedInterests) {
              role.relatedInterests.forEach((interest) => {
                switch (interest.details) {
                  case PersonControlTypeE.DIRS_DIRECT:
                    expect(roleDivs.eq(2).find('[data-cy="control-Directors"]')).to.includes.text('Directors')
                    expect(roleDivs.eq(2).find('[data-cy="control-Directors"]')
                      .find('[data-cy="control-icons-container"]')
                      .find('img[alt="Direct control"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.DIRS_SIG_INFL:
                    expect(roleDivs.eq(2).find('[data-cy="control-Directors"]')).to.includes.text('Directors')
                    expect(roleDivs.eq(2).find('[data-cy="control-Directors"]')
                      .find('[data-cy="control-icons-container"]')
                      .find('img[alt="Significant influence control"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.DIRS_INDIRECT:
                    expect(roleDivs.eq(2).find('[data-cy="control-Directors"]')).to.includes.text('Directors')
                    expect(roleDivs.eq(2).find('[data-cy="control-Directors"]')
                      .find('[data-cy="control-icons-container"]')
                      .find('img[alt="Indirect control (through another business)"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.DIRS_INCONCERT:
                    expect(roleDivs.eq(2).find('[data-cy="control-Directors"]')).to.includes.text('Directors')
                    expect(roleDivs.eq(2).find('[data-cy="control-Directors"]')
                      .find('[data-cy="control-accordian"]')).to.be.an('object')
                    expect(roleDivs.eq(2).find('[data-cy="control-Directors"]')
                      .find('[data-cy="control-accordian"]')
                      .find('[data-cy="control-accordian-inConcert"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.DIR_JOINTLY:
                    expect(roleDivs.eq(2).find('[data-cy="control-Directors"]')).to.includes.text('Directors')
                    expect(roleDivs.eq(2).find('[data-cy="control-Directors"]')
                      .find('[data-cy="control-accordian"]')).to.be.an('object')
                    expect(roleDivs.eq(2).find('[data-cy="control-Directors"]')
                      .find('[data-cy="control-accordian"]')
                      .find('[data-cy="control-accordian-jointly"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.SHARES_BEN_OWNER:
                    expect(roleDivs.eq(2).find('[data-cy="control-Shares"]')).to.includes.text('Shares')
                    expect(roleDivs.eq(2).find('[data-cy="control-Shares"]')
                      .find('[data-cy="control-icons-container"]')
                      .find('img[alt="Beneficial owner"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.SHARES_INDIRECT:
                    expect(roleDivs.eq(2).find('[data-cy="control-Shares"]')).to.includes.text('Shares')
                    expect(roleDivs.eq(2).find('[data-cy="control-Shares"]')
                      .find('[data-cy="control-icons-container"]')
                      .find('img[alt="Indirect control (through another business)"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.SHARES_REG_OWNER:
                    expect(roleDivs.eq(2).find('[data-cy="control-Shares"]')).to.includes.text('Shares')
                    expect(roleDivs.eq(2).find('[data-cy="control-Shares"]')
                      .find('[data-cy="control-icons-container"]')
                      .find('img[alt="Registered owner"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.SHARES_INCONCERT:
                    expect(roleDivs.eq(2).find('[data-cy="control-Shares"]')).to.includes.text('Shares')
                    expect(roleDivs.eq(2).find('[data-cy="control-Shares"]')
                      .find('[data-cy="control-accordian"]')).to.be.an('object')
                    expect(roleDivs.eq(2).find('[data-cy="control-Shares"]')
                      .find('[data-cy="control-accordian"]')
                      .find('[data-cy="control-accordian-inConcert"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.SHARES_JOINTLY:
                    expect(roleDivs.eq(2).find('[data-cy="control-Shares"]')).to.includes.text('Shares')
                    expect(roleDivs.eq(2).find('[data-cy="control-Shares"]')
                      .find('[data-cy="control-accordian"]')).to.be.an('object')
                    expect(roleDivs.eq(2).find('[data-cy="control-Shares"]')
                      .find('[data-cy="control-accordian"]')
                      .find('[data-cy="control-accordian-jointly"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.VOTES_BEN_OWNER:
                    expect(roleDivs.eq(2).find('[data-cy="control-Votes"]')).to.includes.text('Votes')
                    expect(roleDivs.eq(2).find('[data-cy="control-Votes"]')
                      .find('[data-cy="control-icons-container"]')
                      .find('img[alt="Beneficial owner"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.VOTES_INDIRECT:
                    expect(roleDivs.eq(2).find('[data-cy="control-Votes"]')).to.includes.text('Votes')
                    expect(roleDivs.eq(2).find('[data-cy="control-Votes"]')
                      .find('[data-cy="control-icons-container"]')
                      .find('img[alt="Indirect control (through another business)"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.VOTES_REG_OWNER:
                    expect(roleDivs.eq(2).find('[data-cy="control-Votes"]')).to.includes.text('Votes')
                    expect(roleDivs.eq(2).find('[data-cy="control-Votes"]')
                      .find('[data-cy="control-icons-container"]')
                      .find('img[alt="Registered owner"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.VOTES_INCONCERT:
                    expect(roleDivs.eq(2).find('[data-cy="control-Votes"]')).to.includes.text('Votes')
                    expect(roleDivs.eq(2).find('[data-cy="control-Votes"]')
                      .find('[data-cy="control-accordian"]')).to.be.an('object')
                    expect(roleDivs.eq(2).find('[data-cy="control-Votes"]')
                      .find('[data-cy="control-accordian"]')
                      .find('[data-cy="control-accordian-inConcert"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.VOTES_JOINTLY:
                    expect(roleDivs.eq(2).find('[data-cy="control-Votes"]')).to.includes.text('Votes')
                    expect(roleDivs.eq(2).find('[data-cy="control-Votes"]')
                      .find('[data-cy="control-accordian"]')).to.be.an('object')
                    expect(roleDivs.eq(2).find('[data-cy="control-Votes"]')
                      .find('[data-cy="control-accordian"]')
                      .find('[data-cy="control-accordian-inConcert"]')).to.be.an('object')
                    break
                  case PersonControlTypeE.OTHER:
                    expect(roleDivs.eq(2).find('[data-cy="control-Other"]')).to.includes.text('Other')
                    break
                  default:
                    // should be one of the above
                    break
                }
              })
            } else {
              expect(roleDivs.eq(2), 'Details column').to.have.text('')
            }

            // dates
            const date = role.roleDates[0]
            if (role.roleType === 'INCORPORATOR') {
              expect(roleDivs.eq(3), 'Effective Dates column - start').to.have.text(
                date.start ? date.start.substring(0, 10) : 'Unknown')
            } else {
              expect(roleDivs.eq(3), 'Effective Dates column - start').to.include.text(
                date.start ? date.start.substring(0, 10) : 'Unknown')
              expect(roleDivs.eq(3), 'Effective Dates column - end').to.include.text(
                date.end ? date.end.substring(0, 10) : 'Current')
            }
          }
          // actions - will be added back in later
          // expect(cols.eq(7).find('button'), 'Actions column - 1 button').to.have.length(1)
          // expect(cols.eq(7).find('button'), 'Actions column - text').to.include.text('Open')
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
        if (i < 3) {
          cy.get('@firstRow').find('td').eq(Number(i)).invoke('outerWidth').then((bodyWidth) => {
            expect(headerWidth).to.equal(bodyWidth)
          })
        } else {
          cy.get('@firstRow').find('td').eq(3).find('.inner-row-div').eq(0).find('.inner-col-div').eq(Number(i) - 3)
            .invoke('outerWidth').then((bodyWidth) => {
              // NOTE: width of the screen cypress is running is smaller so it is off by more
              expect(headerWidth).to.be.closeTo(bodyWidth, 5)
            })
        }
      })
    }
  })
})
