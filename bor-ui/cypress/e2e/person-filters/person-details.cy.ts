context('filters extended - person details', () => {
  beforeEach(() => {
    cy.visitSearchExtended()
    cy.get('[data-cy="search-radios"]').find('label').eq(1).click()
  })
  it('should trigger a search with the expected payload when updating the filter', () => {
    cy.get('[data-cy="search-results-table"]').should('not.exist')
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .type('test')
    cy.wait('@getSearchResults')
    cy.get('[data-cy="search-results-table"]').should('exist')
    cy.fixture('searchResultsExtended.json').then(() => {
      cy.get('[data-cy="control-filter"]').should('exist')
      cy.get('[data-cy="control-filter-accordion"]').should('not.exist')
      cy.get('[data-cy="control-filter"]')
        .scrollIntoView({ easing: 'linear' })
        .click()
      cy.get('[data-cy="control-filter-accordion"]').should('exist')
      cy.get('[data-cy="control-filter-accordion"]').should('have.length', 4)
      // cy.get('[data-cy="control-filter-accordion"]').eq(0).find('button').should('exist')
      cy.get('[data-cy="control-filter-accordion"]').eq(0).should('have.text', 'Control of Shares')
      cy.get('[data-cy="control-filter-checkbox-controlType.shares.registeredOwner"]')
        .should('not.be.visible')
      cy.get('[data-cy="control-filter-checkbox-controlType.shares.beneficialOwner"]')
        .should('not.be.visible')
      cy.get('[data-cy="control-filter-checkbox-controlType.shares.indirectControl"]')
        .should('not.be.visible')
      cy.get('[data-cy="control-filter-accordion"]').eq(0).click()
      cy.get('[data-cy="control-filter-checkbox-controlType.shares.registeredOwner"]')
        .should('be.visible')
      cy.get('[data-cy="control-filter-checkbox-controlType.shares.beneficialOwner"]')
        .should('be.visible')
      cy.get('[data-cy="control-filter-checkbox-controlType.shares.indirectControl"]')
        .should('be.visible')
      cy.get('[data-cy="control-filter-checkbox-controlType.shares.inConcertControl"]')
        .should('be.visible')
      cy.get('[data-cy="control-filter-checkbox-controlType.shares.actingJointly"]')
        .should('be.visible')

      cy.get('[data-cy="control-filter-checkbox-controlType.shares.registeredOwner"]')
        .click()

      cy.wait('@getSearchResults').then((search) => {
        expect(search).to.have.nested.property('request.body.categories.roles.relatedInterests')
        const relatedInterests = search.request.body.categories.roles.relatedInterests
        expect(relatedInterests).to.have.length(1)
        expect(relatedInterests[0]).to.eql('controlType.shares.registeredOwner')
      })

      cy.get('[data-cy="control-filter-accordion"]').eq(1).should('have.text', 'Control of Votes')
      cy.get('[data-cy="control-filter-accordion"]').eq(1).click()

      cy.get('[data-cy="control-filter-checkbox-controlType.votes.beneficialOwner"]')
        .click()

      cy.wait('@getSearchResults').then((search) => {
        expect(search).to.have.nested.property('request.body.categories.roles.relatedInterests')
        const relatedInterests = search.request.body.categories.roles.relatedInterests
        expect(relatedInterests).to.have.length(2)
        expect(relatedInterests[1]).to.eql('controlType.votes.beneficialOwner')
      })

      cy.get('[data-cy="control-filter-accordion"]').eq(2).should('have.text', 'Control of Directors')
      cy.get('[data-cy="control-filter-accordion"]').eq(2).click()

      cy.get('[data-cy="control-filter-checkbox-controlType.directors.directControl"]')
        .click()

      cy.wait('@getSearchResults').then((search) => {
        expect(search).to.have.nested.property('request.body.categories.roles.relatedInterests')
        const relatedInterests = search.request.body.categories.roles.relatedInterests
        expect(relatedInterests).to.have.length(3)
        expect(relatedInterests[2]).to.eql('controlType.directors.directControl')
      })

      cy.get('[data-cy="control-filter-accordion"]').eq(3).should('have.text', 'Other')
      cy.get('[data-cy="control-filter-accordion"]').eq(3).click()

      cy.get('[data-cy="control-filter-checkbox-other"]')
        .click()

      cy.wait('@getSearchResults').then((search) => {
        expect(search).to.have.nested.property('request.body.categories.roles.relatedInterests')
        const relatedInterests = search.request.body.categories.roles.relatedInterests
        expect(relatedInterests).to.have.length(4)
        expect(relatedInterests[3]).to.eql('other')
      })
    })
  })
})
