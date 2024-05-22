context('App access - logged out', () => {
  it('should render the page with public access', { retries: 5 }, () => {
    sessionStorage.setItem('FAKE_CYPRESS_LOGIN', 'false')
    cy.visit('')
    cy.get('[data-cy="search-page"]').find('h1').should('have.text', 'Business and Person Search')
    cy.get('[data-cy="search-page"]').find('.account-label').should('not.exist')
    cy.get('[data-cy="search-page"]').find('.account-name').should('not.exist')
    cy.get('[data-cy="search-page"]').find('#doc-help-btn').should('have.text', 'Help with Business and Person Search')
  })
})
