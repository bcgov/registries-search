context('App access - unauthorized', () => {
  it('should show access denied when no access', () => {
    cy.visitSearchNoAccess()
    cy.get('[data-cy="base-dialog"]').should('include.text', 'Director Search Access Denied')
  })
})
