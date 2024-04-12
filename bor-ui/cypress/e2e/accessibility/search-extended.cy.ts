context('Accessibility -> Search extended', () => {
  beforeEach(() => {
    cy.visitSearchExtended()
  })

  it('check page passes accessibility before a search', () => {
    // TO-DO: resolve accessibility issues in a future ticket
    cy.checkA11y('[data-cy="search-page"]', {
      rules: {
        'aria-input-field-name': { enabled: false },
        'label-title-only': { enabled: false }
      }
    })
  })

  it('check page passes accessibility after a search is triggered', () => {
    cy.get('[data-cy="search-input"]')
      .find('#search-bar-field')
      .type('test')
    cy.wait('@getSearchResults')

    // TO-DO: resolve accessibility issues in a future ticket
    /* eslint-disable quote-props */
    cy.checkA11y('[data-cy="search-results-table"]', {
      rules: {
        'aria-allowed-attr': { enabled: false },
        'aria-input-field-name': { enabled: false },
        'empty-table-header': { enabled: false },
        'label-title-only': { enabled: false },
        'label': { enabled: false },
        'tabindex': { enabled: false }
      }
    })
  })
})
