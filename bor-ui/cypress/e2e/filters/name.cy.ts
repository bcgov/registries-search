context('filters extended - name', () => {
  beforeEach(() => {
    cy.visitSearchExtended()
  })
  it('should trigger a search with the expected payload when updating the filter', () => {
    cy.get('[data-cy="search-results-table"]').should('not.exist')
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .type('test')
    cy.wait('@getSearchResults')
    cy.get('[data-cy="search-results-table"]').should('exist')
    cy.fixture('searchResultsExtended.json').then(() => {
      const nameFilter = 'a name'
      cy.get('.base-table__header').find('tr').eq(1).find('input').eq(0).type(nameFilter)

      cy.wait('@getSearchResults').then((search) => {
        expect(search).to.have.nested.property('request.body.query')
        expect(search.request.body.query.name).to.equal(nameFilter)
      })
    })
  })
})
