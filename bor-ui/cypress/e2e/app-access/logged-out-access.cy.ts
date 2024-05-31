context('App access - logged out', () => {
  it('should render the page with public access', { retries: 5 }, () => {
    sessionStorage.setItem('FAKE_CYPRESS_LOGIN', 'false')
    cy.visit('')
    cy.get('[data-cy="search-page"]').find('h1').should('have.text', 'Business and Person Search')
    cy.get('[data-cy="search-page"]').find('[data-cy=account-name]').should('not.exist')
    cy.get('[data-cy="search-page"]').find('[data-cy=user-name]').should('not.exist')
    cy.get('[data-cy="search-page"]').find('[data-cy="search-help-btn"]')
      .should('have.text', 'Help with Business and Person Search')
  })
})
