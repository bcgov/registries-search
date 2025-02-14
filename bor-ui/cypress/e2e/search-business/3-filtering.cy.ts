context('Search Business - filtering', () => {
  beforeEach(() => {
    cy.visitSearchPublic()
  })

  it('should trigger a search with the expected payload when updating the filter', () => {
    const queryVal = 'test'
    cy.get('[data-cy="search-input"]')
      .find('[data-cy="search-textfield"]')
      .type(queryVal)
    cy.wait('@getBusinessSearchResults')
    cy.get('[data-cy="search-results-table"]').should('exist')
    cy.fixture('searchResultsBusiness.json').then(() => {
      // filters are there
      cy.get('[data-cy="search-results-table"]')
        .find('.search-table')
        .find('.base-table')
        .find('.base-table__header')
        .find('tr').as('headers')
      cy.get('@headers').should('have.length', 2)
      cy.get('@headers').eq(1).find('.base-table__header__item__filter').as('filters')
      cy.get('@filters').should('have.length', 5)
      // applying filters triggers search with correct payloads
      // business name
      const nameVal = 'k'
      cy.get('@filters').eq(0).find('input').type(nameVal)
      cy.wait('@getBusinessSearchResults').then((search) => {
        expect(search).to.have.nested.property('request.body.query.value')
        expect(search).to.have.nested.property('request.body.query.name')
        expect(search.request.body.query.value).to.eql(queryVal)
        expect(search.request.body.query.name).to.eql(nameVal)
      })
      // identifier
      const identifierVal = 'BC10'
      cy.get('@filters').eq(1).find('input').type(identifierVal)
      cy.wait('@getBusinessSearchResults').then((search) => {
        expect(search).to.have.nested.property('request.body.query.value')
        expect(search).to.have.nested.property('request.body.query.name')
        expect(search).to.have.nested.property('request.body.query.identifier')
        expect(search.request.body.query.value).to.eql(queryVal)
        expect(search.request.body.query.name).to.eql(nameVal)
        expect(search.request.body.query.identifier).to.eql(identifierVal)
      })
      // cra business number
      const bnVal = '123'
      cy.get('@filters').eq(2).find('input').type(bnVal)
      cy.wait('@getBusinessSearchResults').then((search) => {
        expect(search).to.have.nested.property('request.body.query.value')
        expect(search).to.have.nested.property('request.body.query.name')
        expect(search).to.have.nested.property('request.body.query.identifier')
        expect(search).to.have.nested.property('request.body.query.bn')
        expect(search.request.body.query.value).to.eql(queryVal)
        expect(search.request.body.query.name).to.eql(nameVal)
        expect(search.request.body.query.identifier).to.eql(identifierVal)
        expect(search.request.body.query.bn).to.eql(bnVal)
      })
      // business type
      const typeVal = ['C', 'BC']
      cy.get('@filters').eq(3).find('li').should('not.exist')
      // expand list selection
      cy.get('@filters').eq(3).find('button').eq(0).click()
      cy.get('@filters').eq(3).find('li').should('have.length.at.least', 5)
      // select BC Limited
      cy.get('@filters').eq(3).find('li').eq(4).click()
      cy.wait('@getBusinessSearchResults').then((search) => {
        expect(search).to.have.nested.property('request.body.query.value')
        expect(search).to.have.nested.property('request.body.query.name')
        expect(search).to.have.nested.property('request.body.query.identifier')
        expect(search).to.have.nested.property('request.body.query.bn')
        expect(search).to.have.nested.property('request.body.categories.legalType')
        expect(search.request.body.query.value).to.eql(queryVal)
        expect(search.request.body.query.name).to.eql(nameVal)
        expect(search.request.body.query.identifier).to.eql(identifierVal)
        expect(search.request.body.query.bn).to.eql(bnVal)
        expect(search.request.body.categories.legalType).to.eql(typeVal)
      })
      // status
      const statusVal = ['ACTIVE']
      cy.get('@filters').eq(4).find('li').should('not.exist')
      // expand list selection
      cy.get('@filters').eq(4).find('button').eq(0).click()
      cy.get('@filters').eq(4).find('li').should('have.length', 2)
      // select BC Limited
      cy.get('@filters').eq(4).find('li').eq(0).click()
      cy.wait('@getBusinessSearchResults').then((search) => {
        expect(search).to.have.nested.property('request.body.query.value')
        expect(search).to.have.nested.property('request.body.query.name')
        expect(search).to.have.nested.property('request.body.query.identifier')
        expect(search).to.have.nested.property('request.body.query.bn')
        expect(search).to.have.nested.property('request.body.categories.legalType')
        expect(search).to.have.nested.property('request.body.categories.status')
        expect(search.request.body.query.value).to.eql(queryVal)
        expect(search.request.body.query.name).to.eql(nameVal)
        expect(search.request.body.query.identifier).to.eql(identifierVal)
        expect(search.request.body.query.bn).to.eql(bnVal)
        expect(search.request.body.categories.legalType).to.eql(typeVal)
        expect(search.request.body.categories.status).to.eql(statusVal)
      })
      // siginificant individuals
      // NOTE: will be added back in later
      // const siVal = 'si'
      // cy.get('@filters').eq(5).find('input').type(siVal)
      // cy.wait('@getBusinessSearchResults').then((search) => {
      //   expect(search).to.have.nested.property('request.body.query.value')
      //   expect(search).to.have.nested.property('request.body.query.name')
      //   expect(search).to.have.nested.property('request.body.query.identifier')
      //   expect(search).to.have.nested.property('request.body.query.bn')
      //   expect(search).to.have.nested.property('request.body.categories.legalType')
      //   expect(search).to.have.nested.property('request.body.categories.status')
      //   expect(search).to.have.nested.property('request.body.query.parties.partyName')
      //   expect(search.request.body.query.value).to.eql(queryVal)
      //   expect(search.request.body.query.name).to.eql(nameVal)
      //   expect(search.request.body.query.identifier).to.eql(identifierVal)
      //   expect(search.request.body.query.bn).to.eql(bnVal)
      //   expect(search.request.body.categories.legalType).to.eql(typeVal)
      //   expect(search.request.body.categories.status).to.eql(statusVal)
      //   expect(search.request.body.query.parties.partyName).to.eql(siVal)
      // })
      // clear 1 select filter
      cy.get('@filters').eq(3).find('button').eq(1).click()
      cy.wait('@getBusinessSearchResults').then((search) => {
        expect(search).to.have.nested.property('request.body.query.value')
        expect(search).to.have.nested.property('request.body.query.name')
        expect(search).to.have.nested.property('request.body.query.identifier')
        expect(search).to.have.nested.property('request.body.query.bn')
        expect(search).to.have.nested.property('request.body.categories.legalType')
        expect(search).to.have.nested.property('request.body.categories.status')
        // expect(search).to.have.nested.property('request.body.query.parties.partyName')
        expect(search.request.body.query.value).to.eql(queryVal)
        expect(search.request.body.query.name).to.eql(nameVal)
        expect(search.request.body.query.identifier).to.eql(identifierVal)
        expect(search.request.body.query.bn).to.eql(bnVal)
        // this value changed, others should be the same
        expect(search.request.body.categories.legalType).to.eql([])
        expect(search.request.body.categories.status).to.eql(statusVal)
        // expect(search.request.body.query.parties.partyName).to.eql(siVal)
      })
      // clear 1 text filter
      cy.get('@filters').eq(0).find('button').eq(0).click()
      cy.wait('@getBusinessSearchResults').then((search) => {
        expect(search).to.have.nested.property('request.body.query.value')
        expect(search).to.have.nested.property('request.body.query.name')
        expect(search).to.have.nested.property('request.body.query.identifier')
        expect(search).to.have.nested.property('request.body.query.bn')
        expect(search).to.have.nested.property('request.body.categories.legalType')
        expect(search).to.have.nested.property('request.body.categories.status')
        // expect(search).to.have.nested.property('request.body.query.parties.partyName')
        expect(search.request.body.query.value).to.eql(queryVal)
        // this value changed, others should be the same
        expect(search.request.body.query.name).to.eql('')
        expect(search.request.body.query.identifier).to.eql(identifierVal)
        expect(search.request.body.query.bn).to.eql(bnVal)
        expect(search.request.body.categories.legalType).to.eql([])
        expect(search.request.body.categories.status).to.eql(statusVal)
        // expect(search.request.body.query.parties.partyName).to.eql(siVal)
      })
      // clear all filters
      cy.get('[data-cy="search-table-clear-filters"]').should('be.visible')
      cy.get('[data-cy="search-table-clear-filters"]').click()
      cy.wait('@getBusinessSearchResults').then((search) => {
        expect(search).to.have.nested.property('request.body.query.value')
        expect(search).to.not.have.nested.property('request.body.query.name')
        expect(search).to.not.have.nested.property('request.body.query.identifier')
        expect(search).to.not.have.nested.property('request.body.query.bn')
        expect(search).to.not.have.nested.property('request.body.categories.status')
        // expect(search).to.not.have.nested.property('request.body.query.parties.partyName')
        expect(search).to.have.nested.property('request.body.categories.legalType')
        expect(search.request.body.query.value).to.eql(queryVal)
        expect(search.request.body.categories.legalType).to.eql([])
      })
    })
  })
})
