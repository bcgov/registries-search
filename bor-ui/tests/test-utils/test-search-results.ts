import type { SearchResultI } from '@/interfaces/search-i'

export const testSearchResultInterest: SearchResultI[] = [
  {
    entityAddresses: [{
      addressCity: 'Oakville',
      addressCountry: 'Canada',
      addressRegion: 'ON',
      postalCode: 'L6M 3G8',
      streetAddress: '1232-1490 Pilgrims Way ',
      locationDescription: ''
    }],
    entityType: 'PERSON',
    legalName: 'ALL INTEREST TEST',
    roles: [{
      active: true,
      relatedBN: '123456777BC0001',
      relatedEmail: 'coop@email.com',
      relatedEntityType: 'BUSINESS',
      relatedIdentifier: 'CP1234567',
      relatedLegalType: 'CP',
      relatedName: 'KIALS COOP',
      relatedState: 'ACTIVE',
      relatedInterests: [
        {
          details: 'controlType.sharesOrVotes.beneficialOwner',
          interestType: 'shareholding',
          sharesMin: 25,
          sharesMax: 50
        },
        {
          details: 'controlType.sharesOrVotes.beneficialOwner',
          interestType: 'votingRights',
          sharesMin: 25,
          sharesMax: 50
        },
        {
          details: 'controlType.sharesOrVotes.indirectControl',
          interestType: 'shareholding',
          sharesMin: 25,
          sharesMax: 50
        },
        {
          details: 'controlType.sharesOrVotes.indirectControl',
          interestType: 'votingRights',
          sharesMin: 25,
          sharesMax: 50
        },
        {
          details: 'controlType.sharesOrVotes.inConcertControl',
          interestType: 'shareholding',
          sharesMin: 25,
          sharesMax: 50
        },
        {
          details: 'controlType.sharesOrVotes.inConcertControl',
          interestType: 'votingRights',
          sharesMin: 25,
          sharesMax: 50
        },
        {
          details: 'controlType.sharesOrVotes.registeredOwner',
          interestType: 'shareholding',
          sharesMin: 25,
          sharesMax: 50
        },
        {
          details: 'controlType.sharesOrVotes.registeredOwner',
          interestType: 'votingRights',
          sharesMin: 25,
          sharesMax: 50
        },
        // other
        {
          details: 'Test',
          interestType: 'otherInfluenceOrControl',
          sharesMin: 25,
          sharesMax: 50
        },
        // directors
        {
          details: 'controlType.directors.significantInfluence',
          interestType: 'appointmentOfBoard'
        },
        {
          details: 'controlType.directors.indirectControl',
          interestType: 'appointmentOfBoard'
        },
        {
          details: 'controlType.directors.inConcertControl',
          interestType: 'appointmentOfBoard'
        },
        {
          details: 'controlType.directors.directControl',
          interestType: 'appointmentOfBoard'
        }
      ],
      roleDates: [{ start: new Date('2022-06-28T00:00:00') }],
      roleType: 'DIRECTOR'
    }]
  }
]

export const testSearchResults: SearchResultI[] = [
  {
    alternateName: 'Waffle Wallaby',
    birthDate: '1958-04-22',
    email: 'email@email.com',
    entityAddresses: [{
      addressCity: 'Vancouver',
      addressCountry: 'Canada',
      addressRegion: 'BC',
      postalCode: 'V6L 4V9',
      streetAddress: '99 Waffles street',
      locationDescription: 'Unit 201, Building A'
    }],
    entityType: 'PERSON',
    isPR: false,
    legalName: 'KIAL TEST',
    nationalities: ['CA', 'US'],
    roles: [{
      active: true,
      relatedAddresses: [{
        addressCity: 'Victoria',
        addressCountry: 'Canada',
        addressRegion: 'BC',
        postalCode: 'V2M 7W0',
        streetAddress: '224 Sleepy Lane',
        streetAdditional: 'Fun Place',
        locationDescription: 'Dogs in the backyard'
      }],
      relatedBN: '123456789BC0001',
      relatedEmail: 'test@email.com',
      relatedEntityType: 'BUSINESS',
      relatedIdentifier: 'BC0871105',
      relatedInterests: [{
        interestType: 'shareholding',
        details: 'controlType.sharesOrVotes.beneficialOwner',
        sharesMax: 50,
        sharesMin: 25
      }],
      relatedLegalType: 'BC',
      relatedName: 'AA 0871105 B.C. LTD.',
      relatedState: 'ACTIVE',
      roleDates: [
        { start: new Date('2020-06-28T00:00:00') },
        { start: new Date('2019-02-19T00:00:00'), end: new Date('2019-06-09T00:00:00') }
      ],
      roleType: 'SIGNIFICANT INDIVIDUAL'
    },
    {
      active: true,
      relatedAddresses: [{
        addressCountry: '',
        addressRegion: null,
        streetAddress: '',
        streetAdditional: 'Lost my glasses',
        locationDescription: 'Where am I'
      }],
      relatedBN: '123456789BC0002',
      relatedEmail: 'test@email.com',
      relatedEntityType: 'BUSINESS',
      relatedIdentifier: 'BC0871105',
      relatedInterests: [{
        details: 'controlType.sharesOrVotes.beneficialOwner',
        interestType: 'votingRights',
        sharesMin: 25,
        sharesMax: 50
      },
      {
        details: 'controlType.sharesOrVotes.indirectControl',
        interestType: 'shareholding',
        sharesMin: 25,
        sharesMax: 50
      },
      {
        details: 'controlType.sharesOrVotes.indirectControl',
        interestType: 'votingRights',
        sharesMin: 25,
        sharesMax: 50
      }],
      relatedLegalType: 'BC',
      relatedName: 'BB 0871106 B.C. LTD.',
      relatedState: 'ACTIVE',
      roleDates: [
        { start: new Date('2010-01-10T00:00:00'), end: new Date('2016-07-11T00:00:00') },
        { start: new Date('2022-01-10T00:00:00') },
        { start: new Date('2018-02-21T00:00:00'), end: new Date('2019-05-11T00:00:00') }
      ],
      roleType: 'DIRECTOR'
    },
    {
      active: true,
      relatedBN: '123456789BC0003',
      relatedEmail: 'test@email.com',
      relatedEntityType: 'BUSINESS',
      relatedIdentifier: 'BC0871107',
      relatedInterests: [{
        interestType: 'shareholding',
        details: 'controlType.sharesOrVotes.beneficialOwner',
        sharesMax: 50,
        sharesMin: 25
      }],
      relatedLegalType: 'BC',
      relatedName: 'CC 0871105 B.C. LTD.',
      relatedState: 'ACTIVE',
      roleDates: [{ start: new Date('2020-06-29T00:00:00Z') }],
      roleType: 'SIGNIFICANT INDIVIDUAL'
    }],
    taxNumber: '123 456 789',
    taxResidencies: ['CA']
  },
  {
    entityAddresses: [{
      addressCity: 'Oakville',
      addressCountry: 'Canada',
      addressRegion: 'ON',
      postalCode: 'L6M 3G8',
      streetAddress: '1232-1490 Pilgrims Way ',
      locationDescription: ''
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
      roleDates: [{ start: new Date('2022-06-28T00:00:00') }],
      roleType: 'DIRECTOR'
    }]
  },
  {
    entityAddresses: [{
      addressCity: 'Oakville',
      addressCountry: 'Canada',
      addressRegion: 'ON',
      postalCode: 'L6M 3G8',
      streetAddress: '1232-1490 Pilgrims Way ',
      locationDescription: ''
    }],
    entityType: 'PERSON',
    legalName: 'KIAL TEST 2',
    roles: [{
      active: true,
      relatedAddresses: [{
        addressCity: 'Victoria',
        addressCountry: 'Canada',
        addressRegion: 'BC',
        postalCode: 'V2M 7W0',
        streetAddress: '123 Normal Street'
      }],
      relatedEntityType: 'BUSINESS',
      relatedIdentifier: 'BC0871105',
      relatedLegalType: 'BC',
      relatedName: '0871105 B.C. LTD.',
      relatedState: 'ACTIVE',
      roleDates: [{
        start: new Date('2016-03-28T00:00:00'),
        end: new Date('2023-03-28T00:00:00')
      }],
      roleType: 'OFFICER'
    }]
  },
  {
    entityAddresses: [{
      addressCity: 'Oakville',
      addressCountry: 'Canada',
      addressRegion: 'ON',
      postalCode: 'L6M 3G8',
      streetAddress: '1232-1490 Pilgrims Way ',
      locationDescription: ''
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
      roleDates: [{ start: new Date('2022-06-28T00:00:00') }],
      roleType: 'DIRECTOR'
    }]
  },
  testSearchResultInterest[0]
]
