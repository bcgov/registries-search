context('App access - extended', () => {
  it('should render the competent authority search page when account has extended access', () => {
    cy.visitSearchExtended()
    cy.get('[data-cy="search-page"]').find('h1').should('have.text', 'Business and Person Search')
    cy.get('[data-cy="search-page"]').find('[data-cy=account-name]').should('have.text', 'test Dev 1')
    cy.get('[data-cy="search-page"]').find('[data-cy=user-name]').should('have.text', 'TestFirst TestLast')
    cy.get('[data-cy="search-page"]').find('[data-cy="search-help-btn"]')
      .should('have.text', 'Help with Business and Person Search')
    cy.get('[data-cy="search-radios"]').find('label').should('have.length', 3)
    cy.get('[data-cy="search-radios"]').find('label').eq(0).should('have.text', 'Search Businesses')
    cy.get('[data-cy="search-radios"]').find('label').eq(1).should('have.text', 'Search People')
    cy.get('[data-cy="search-radios"]').find('label').eq(2).should('have.text', 'Search Directors')
  })
})
