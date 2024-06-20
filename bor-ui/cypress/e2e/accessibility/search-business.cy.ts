context('Accessibility -> Search public', () => {
  beforeEach(() => {
    cy.visitSearchPublic()
  })

  it('check page passes accessibility before a search', () => {
    // TO-DO: resolve accessibility issues in a future ticket: #20860
    cy.checkA11y('[data-cy="search-page"]')
  })

  it('check page passes accessibility after a search is triggered', () => {
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .type('test')
    cy.wait('@getBusinessSearchResults')

    // TO-DO: resolve accessibility issues in a future ticket: #20859
    // nuxt/ui nested-interactive issue: https://github.com/nuxt/ui/issues/1428
    cy.checkA11y('[data-cy="search-results-table"]', {
      rules: {
        'empty-table-header': { enabled: false },
        'nested-interactive': { enabled: false }
      }
    })
  })
})
