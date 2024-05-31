context('App access - basic', () => {
  it('should render the director search page when account has basic access', () => {
    cy.visitSearchLimited()
    cy.get('[data-cy="search-page"]').find('h1').should('have.text', 'Director Search')
    cy.get('[data-cy="search-page"]').find('[data-cy=account-name]').should('have.text', 'test Dev 1')
    cy.get('[data-cy="search-page"]').find('[data-cy=user-name]').should('have.text', 'TestFirst TestLast')
    cy.get('[data-cy="search-page"]').find('[data-cy="search-help-btn"]')
      .should('have.text', 'Help with Director Search')
  })
})
