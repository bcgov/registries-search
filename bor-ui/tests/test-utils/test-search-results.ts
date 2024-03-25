export const testSearchResults: SearchResultI[] = [
  {
    alternateName: 'Waffle Wallaby',
    birthDate: '1958-04-22',
    email: 'email@email.com',
    entityAddresses: [{
      addressCity: 'Vancouver',
      addressCountry: 'CA',
      addressRegion: 'BC',
      postalCode: 'V6L 4V9',
      streetAddress: '99 Waffles street'
    }],
    entityType: 'PERSON',
    isPR: false,
    legalName: 'KIAL TEST',
    nationalities: ['CA'],
    roles: [{
      active: true,
      relatedBN: '123456789BC0001',
      relatedEmail: 'test@email.com',
      relatedEntityType: 'BUSINESS',
      relatedIdentifier: 'BC0871105',
      relatedInterests: [{
        type: 'shareholding',
        details: 'control.registeredOwner',
        shareMax: 50,
        shareMin: 25
      }],
      relatedLegalType: 'BC',
      relatedName: '0871105 B.C. LTD.',
      relatedState: 'ACTIVE',
      roleDates: [{ start: new Date('2020-06-28T00:00:00Z') }],
      roleType: 'SIGNIFICANT INDIVIDUAL'
    }],
    taxNumber: '123 456 789',
    taxResidencies: ['CA']
  },
  {
    entityAddresses: [{
      addressCity: 'Oakville',
      addressCountry: 'CA',
      addressRegion: 'ON',
      postalCode: 'L6M 3G8',
      streetAddress: '1232-1490 Pilgrims Way '
    }],
    entityType: 'PERSON',
    legalName: 'KIAL TEST',
    roles: [{
      active: true,
      relatedBN: '123456789BC0001',
      relatedEmail: 'test@email.com',
      relatedEntityType: 'BUSINESS',
      relatedIdentifier: 'BC0871105',
      relatedLegalType: 'BC',
      relatedName: '0871105 B.C. LTD.',
      relatedState: 'ACTIVE',
      roleDates: [{ start: new Date('2022-06-28T00:00:00Z') }],
      roleType: 'DIRECTOR'
    }]
  },
  {
    entityAddresses: [{
      addressCity: 'Oakville',
      addressCountry: 'CA',
      addressRegion: 'ON',
      postalCode: 'L6M 3G8',
      streetAddress: '1232-1490 Pilgrims Way '
    }],
    entityType: 'PERSON',
    legalName: 'KIAL TEST 2',
    roles: [{
      active: true,
      relatedEntityType: 'BUSINESS',
      relatedIdentifier: 'BC0871105',
      relatedLegalType: 'BC',
      relatedName: '0871105 B.C. LTD.',
      relatedState: 'ACTIVE',
      roleDates: [{ start: new Date('2016-03-28T00:00:00Z'), end: new Date('2023-03-28T00:00:00Z') }],
      roleType: 'OFFICER'
    }]
  },
  {
    entityAddresses: [{
      addressCity: 'Oakville',
      addressCountry: 'CA',
      addressRegion: 'ON',
      postalCode: 'L6M 3G8',
      streetAddress: '1232-1490 Pilgrims Way '
    }],
    entityType: 'PERSON',
    legalName: 'KIAL TEST',
    roles: [{
      active: true,
      relatedBN: '123456777BC0001',
      relatedEmail: 'coop@email.com',
      relatedEntityType: 'BUSINESS',
      relatedIdentifier: 'CP1234567',
      relatedLegalType: 'CP',
      relatedName: 'KIALS COOP',
      relatedState: 'ACTIVE',
      roleDates: [{ start: new Date('2022-06-28T00:00:00Z') }],
      roleType: 'DIRECTOR'
    }]
  }
]
