context('filters extended - citizenship', () => {
  beforeEach(() => {
    cy.visitSearchExtended()
  })
  it('should trigger a search with the expected payload when updating the filter', () => {
    cy.get('[data-cy="search-results-table"]').should('not.exist')
    cy.get('[data-cy="search-input"]')
      .find('#search-bar-field')
      .type('test')
    cy.wait('@getSearchResults')
    cy.get('[data-cy="search-results-table"]').should('exist')
    cy.fixture('searchResultsExtended.json').then(() => {
      const citzSelection = 'Canada'
      cy.get('.base-table__header').find('tr').eq(1).find('th').eq(2).find('.base-table__header__item__filter').click()
      cy.get('.v-overlay__content.v-select__content').find('.v-list').find('.v-list-item').eq(0)
        .should('have.text', citzSelection)
      cy.get('.v-overlay__content.v-select__content').find('.v-list').find('.v-list-item').eq(0).click()
      cy.get('.base-table__header').find('tr').eq(1).find('th').eq(2).find('.base-table__header__item__filter')
        .find('.flag.f-ca').should('exist')

      cy.wait('@getSearchResults').then((search) => {
        expect(search?.request?.body?.query !== undefined)
        expect(search.request.body.categories.nationalities).to.eql(['CA'])
      })
    })
  })
})
