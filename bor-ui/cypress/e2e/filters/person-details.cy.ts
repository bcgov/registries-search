context('filters extended - person details', () => {
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
        expect(search).to.have.nested.property('request.body.categories.roles.relatedInterests')
        const relatedInterests = search.request.body.categories.roles.relatedInterests
        expect(relatedInterests).to.have.length(1)
        expect(relatedInterests[0]).to.eql('controlType.sharesOrVotes.registeredOwner')
      })
    })
  })
})
