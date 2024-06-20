context('Accessibility -> Search public', () => {
  beforeEach(() => {
    cy.visitSearchPublic()
    // click 'search owners' radio
    cy.get('[data-cy="search-radios"]').find('label').eq(1).click()
  })

  it('check page passes accessibility before a search', () => {
    // TO-DO: resolve accessibility issues in a future ticket: #20860
    cy.checkA11y('[data-cy="search-page"]')
  })

  it('check page passes accessibility after a search is triggered', () => {
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .type('test')
    cy.wait('@getSearchResults')

    // TO-DO: resolve accessibility issues in a future ticket: #20859
    // nuxt/ui nested-interactive issue: https://github.com/nuxt/ui/issues/1428
    /* eslint-disable quote-props */
    cy.checkA11y('[data-cy="search-results-table"]', {
      rules: {
        'color-contrast': { enabled: false },
        'tabindex': { enabled: false },
        'nested-interactive': { enabled: false }
      }
    })
  })
})
