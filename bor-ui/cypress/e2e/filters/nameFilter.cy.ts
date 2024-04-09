context('Search extended', () => {
  beforeEach(() => {
    cy.visitSearchExtended()
  })
  it('should display expected results after a search is triggered', () => {
    cy.get('[data-cy="search-results-table"]').should('not.exist')
    cy.get('[data-cy="search-input"]')
      .find('#search-bar-field')
      .type('test')
    cy.wait('@getSearchResults')
    cy.get('[data-cy="search-results-table"]').should('exist')
    cy.fixture('searchResultsExtended.json').then(() => {
      const nameFilter = 'a name'
      cy.get('.base-table__header').find('tr').eq(1).find('input').eq(0).type(nameFilter)

      cy.wait('@getSearchResults').then((search) => {
        expect(search?.request?.body?.query !== undefined)
        expect(search.request.body.query.name === nameFilter)
      })
    })
  })
})
