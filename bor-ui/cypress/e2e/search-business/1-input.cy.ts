context('Search Business - input', () => {
  beforeEach(() => {
    cy.visitSearchPublic()
  })

  it('should display expected search bar', () => {
    // info text
    cy.get('[data-cy="search-input-info-text"]').should(
      'have.text',
      'Search for businesses registered or incorporated in B.C. and access their business documents.'
    )
    // search input
    cy.get('[data-cy="search-input"]').find('[data-cy="search-textfield"]').should('exist')
    // label text
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .should('have.attr', 'placeholder', 'Business Name or Incorporation/Registration Number or CRA Business Number')
    // hint text
    cy.get('[data-cy="search-input"]')
      .find('p')
      .should(
        'have.text',
        'Example: "Test Construction Inc.", "BC0000123", "987654321BC001"')
  })
})
