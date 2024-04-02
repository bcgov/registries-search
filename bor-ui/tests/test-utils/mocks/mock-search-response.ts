export const SearchResponseMock = {
  facets: {
    fields: {
      addressCity: [{ count: 1, parentCount: 1, value: 'Oakville' }, { count: 1, parentCount: 1, value: 'Coquitlam' }],
      addressCountry: [{ count: 1, parentCount: 2, value: 'CA' }],
      addressRegion: [{ count: 1, parentCount: 1, value: 'ON' }, { count: 1, parentCount: 1, value: 'BC' }],
      entityType: [{ count: 2, value: 'PERSON' }, { count: 1, value: 'BUSINESS' }],
      legalType: [{ count: 1, value: 'BEN' }],
      relatedEntityType: [{ count: 1, parentCount: 1, value: 'BUSINESS' }],
      relatedLegalType: [{ count: 1, parentCount: 1, value: 'BEN' }],
      relatedState: [{ count: 1, parentCount: 1, value: 'ACTIVE' }],
      roleType: [{ count: 1, parentCount: 1, value: 'DIRECTOR' }],
      state: [{ count: 1, value: 'ACTIVE' }]
    }
  },
  searchResults: {
    queryInfo: {
      categories: {
        entityAddresses: { addressCity: null, addressCountry: null, addressRegion: null },
        entityType: ['PERSON'],
        legalType: null,
        roles: { relatedEntityType: null, relatedState: null, roleType: null },
        state: null
      },
      query: {
        bn: '',
        entityAddresses: '',
        identifier: '',
        legalName: '',
        roles: { relatedBN: '', relatedIdentifier: '', relatedName: '', roleDates: {} },
        value: 'kial'
      },
      rows: 100,
      start: 0
    },
    results: [
      {
        entityAddresses: [{
          addressCity: 'Oakville',
          addressCountry: 'CA',
          addressRegion: 'ON',
          addressType: 'DELIVERY',
          postalCode: 'L6M 3G8',
          score: 0.0,
          streetAddress: '1232-1490 Pilgrims Way '
        }],
        entityType: 'PERSON',
        legalName: 'KIAL TEST',
        nationalities: ['CA'],
        roles: [{
          active: true,
          relatedBN: '123456789BC0001',
          relatedEmail: 'test@email.com',
          relatedEntityType: 'BUSINESS',
          relatedIdentifier: 'BC0871105',
          relatedLegalType: 'BC',
          relatedName: '0871105 B.C. LTD.',
          relatedState: 'ACTIVE',
          roleDates: [
            { score: 0.0, start: '2022-06-28T00:00:00Z' },
            { score: 0.0, start: '2018-01-01T00:00:00Z', end: '2021-01-01T00:00:00Z' },
            { score: 0.0, start: '2012-01-01T00:00:00Z', end: '2013-01-01T00:00:00Z' }
          ],
          roleType: 'DIRECTOR',
          score: 0.0
        }],
        score: 42.551533
      },
      {
        entityAddresses: [{
          addressCity: 'Vancouver',
          addressCountry: 'CA',
          addressRegion: 'BC',
          addressType: 'DELIVERY',
          postalCode: 'V1V 5A6',
          score: 0.0,
          streetAddress: '123 16th Avenue'
        }],
        entityType: 'PERSON',
        legalName: 'TEST NAME',
        nationalities: ['US', 'GB', 'FR'],
        roles: [{
          active: true,
          relatedBN: '123456789BC0001',
          relatedEmail: 'test@email.com',
          relatedEntityType: 'BUSINESS',
          relatedIdentifier: 'BC0871105',
          relatedLegalType: 'BC',
          relatedName: '0871105 B.C. LTD.',
          relatedState: 'ACTIVE',
          roleDates: [
            { score: 0.0, start: '2018-01-01T00:00:00Z', end: '2021-01-01T00:00:00Z' },
            { score: 0.0, end: '2014-01-01T00:00:00Z' }
          ],
          roleType: 'SIGNIFICANT INDIVIDUAL',
          score: 0.0
        }],
        score: 42.551533
      },
      {
        entityAddresses: [{
          addressCity: 'Oakville',
          addressCountry: 'CA',
          addressRegion: 'ON',
          addressType: 'DELIVERY',
          postalCode: 'L6M 3G8',
          score: 0.0,
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
          roleDates: [{ score: 0.0, end: '2023-03-28T00:00:00Z' }],
          roleType: 'OFFICER',
          score: 0.0
        }],
        score: 42.551533
      },
      {
        bn: '123456789BC0001',
        entityAddresses: [
          {
            addressCity: 'Coquitlam',
            addressCountry: 'CA',
            addressRegion: 'BC',
            addressType: 'DELIVERY',
            postalCode: 'V3K 3V9',
            score: 0,
            streetAddress: 'Bc-435 North Rd'
          }
        ],
        entityType: 'BUSINESS',
        identifier: 'BC0871330',
        legalName: 'KIALS BUSINESS NAME CORP.',
        legalType: 'BEN',
        score: 11.459389,
        state: 'ACTIVE'
      },
      {
        entityAddresses: [{
          addressCity: 'Oakville',
          addressCountry: 'CA',
          addressRegion: 'ON',
          addressType: 'DELIVERY',
          postalCode: 'L6M 3G8',
          score: 0.0,
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
          roleDates: [{ score: 0.0, start: '2022-06-28T00:00:00Z' }],
          roleType: 'DIRECTOR',
          score: 0.0
        }],
        score: 42.551533
      }
    ],
    totalResults: 5
  }
}
