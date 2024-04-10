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
      cy.get('[data-cy="details-filter"]').should('exist')
      cy.get('[data-cy="details-filter-shares-votes"]').should('not.exist')
      cy.get('[data-cy="details-filter-textbox"]')
        .scrollIntoView({ easing: 'linear' })
        .click()
      cy.get('[data-cy="details-filter-shares-votes"]')
        .click()
      cy.get('[data-cy="details-filter-shares-votes-registered-owner"]')
        .find('input')
        .click()

      cy.wait('@getSearchResults').then((search) => {
        expect(search?.request?.body?.categories?.roles?.relatedInterests !== undefined)
        const relatedInterests = search.request.body.categories.roles.relatedInterests
        expect(relatedInterests.length === 1)
        expect(relatedInterests.length[0] === 'controlType.sharesOrVotes.registeredOwner')
      })
    })
  })
})
