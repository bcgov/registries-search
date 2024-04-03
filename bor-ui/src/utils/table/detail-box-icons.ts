import { SearchIconsE } from '@/enums/search-icons-e'
import type { ControlColumnIconI } from '@/interfaces/person-search-table'

export const convertDetailsToIcon = (details: string): ControlColumnIconI => {
  switch (details) {
    // share control
    // votes control
    case 'controlType.sharesOrVotes.beneficialOwner': {
      return {
        src: SearchIconsE.SHARES_VOTES_BENEFICIAL_OWNER,
        alt: 'Beneficial owner (e.g., through a trust)',
        tooltip: 'Beneficial owner (e.g., through a trust)'
      }
    }
    case 'controlType.sharesOrVotes.indirectControl':
    case 'controlType.sharesOrVotes.inConcertControl': {
      return {
        src: SearchIconsE.SHARES_VOTES_INDIRECT_CONTROL,
        alt: 'Indirect control (e.g., through another business)',
        tooltip: 'Indirect control (e.g., through another business)'
      }
    }
    case 'controlType.sharesOrVotes.registeredOwner': {
      return {
        src: SearchIconsE.SHARES_VOTES_REGISTERED_OWNER,
        alt: 'Registered owner',
        tooltip: 'Registered owner'
      }
    }
    // directors control
    case 'controlType.directors.directControl': {
      return {
        src: SearchIconsE.DIRECTORS_DIRECT_CONTROL,
        alt: 'Direct control',
        tooltip: 'Direct control'
      }
    }
    case 'controlType.directors.inConcertControl': {
      return {
        src: SearchIconsE.DIRECTORS_CONTROL_MAJORITY_OF_DIRECTORS,
        alt: 'This individual has control of the majority of directors through rights and/or exercised in concert ' +
          'with other individuals',
        tooltip: 'This individual has control of the majority of directors through rights and/or exercised in ' +
          'concert with other individuals'
      }
    }
    case 'controlType.directors.indirectControl': {
      return {
        src: SearchIconsE.DIRECTORS_INDIRECT_CONTROL,
        alt: 'Indirect control (through another business)',
        tooltip: 'Indirect control (through another business)'
      }
    }
    case 'controlType.directors.significantInfluence': {
      return {
        src: SearchIconsE.DIRECTORS_SIGNIFICANT_INFLUENCE_CONTROL,
        alt: 'Significant influence control',
        tooltip: 'Significant influence control'
      }
    }
    default: {
      return null
    }
  }
}

export const OtherControlIcon = {
  src: SearchIconsE.OTHER,
  alt: 'Any other reason(s) this individual is a significant individual',
  tooltip: 'Any other reason(s) this individual is a significant individual'
}
