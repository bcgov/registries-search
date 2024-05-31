Cypress.Commands.add('visitSearchPublic', () => {
  sessionStorage.setItem('FAKE_CYPRESS_LOGIN', 'true')
  cy.intercept('GET', '**/api/v1/users/**/settings', { fixture: 'settings.json' }).as('getSettings')
  cy.intercept(
    'REPORT',
    'https://app.launchdarkly.com/sdk/evalx/**/context',
    { fixture: 'ldarklyContext.json' }
  ).as('getLdarklyContext')
  cy.intercept('GET', '**/api/v1/orgs/**/products*', { fixture: 'productsNone.json' }).as('getProducts')
  cy.interceptSearch('/public', 'searchResultsPublic.json')
  cy.visit('')
  cy.wait(['@getSettings', '@getProducts'])
  cy.injectAxe()
})

Cypress.Commands.add('visitSearchLimited', () => {
  sessionStorage.setItem('FAKE_CYPRESS_LOGIN', 'true')
  cy.intercept('GET', '**/api/v1/users/**/settings', { fixture: 'settings.json' }).as('getSettings')
  cy.intercept(
    'REPORT',
    'https://app.launchdarkly.com/sdk/evalx/**/context',
    { fixture: 'ldarklyContext.json' }
  ).as('getLdarklyContext')
  cy.intercept('GET', '**/api/v1/orgs/**/products*', { fixture: 'productsBasic.json' }).as('getProducts')
  cy.interceptSearch('', 'searchResultsLimited.json')
  cy.visit('')
  cy.wait(['@getSettings', '@getProducts'])
  cy.injectAxe()
})

Cypress.Commands.add('visitSearchExtended', () => {
  sessionStorage.setItem('FAKE_CYPRESS_LOGIN', 'true')
  cy.intercept('GET', '**/api/v1/users/**/settings', { fixture: 'settings.json' }).as('getSettings')
  cy.intercept(
    'REPORT',
    'https://app.launchdarkly.com/sdk/evalx/**/context',
    { fixture: 'ldarklyContext.json' }
  ).as('getLdarklyContext')
  cy.intercept('GET', '**/api/v1/orgs/**/products*', { fixture: 'productsExtended.json' }).as('getProducts')
  cy.interceptSearch('/extended', 'searchResultsExtended.json')
  cy.visit('')
  cy.wait(['@getSettings', '@getProducts'])
  cy.injectAxe()
})

Cypress.Commands.add('visitSearchAuthError', () => {
  sessionStorage.setItem('FAKE_CYPRESS_LOGIN', 'true')
  cy.intercept('GET', '**/api/v1/users/**/settings', { statusCode: 500, body: {} }).as('getSettingsError')
  cy.intercept(
    'REPORT',
    'https://app.launchdarkly.com/sdk/evalx/**/context',
    { fixture: 'ldarklyContext.json' }
  ).as('getLdarklyContext')
  cy.visit('')
  cy.wait(['@getSettingsError'])
  cy.injectAxe()
})

Cypress.Commands.add('interceptSearch', (path: string, fixtureFileName: string) => {
  cy.intercept('POST', '**/api/v1/search' + path, { fixture: fixtureFileName }).as('getSearchResults')
})
