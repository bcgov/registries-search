context('App access - logged out', () => {
  it('should redirect logged out users to login site', { retries: 5 }, () => {
    sessionStorage.setItem('FAKE_CYPRESS_LOGIN', 'false')
    cy.visit('')
    cy.origin('https://dev.bcregistry.gov.bc.ca', () => {
      cy.url().should('include', 'login')
    })
  })
})
