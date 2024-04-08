import { PersonControlTypeE } from '@/enums/person-control-type-e'
import { SearchIconsE } from '@/enums/search-icons-e'
import type { ControlColumnIconI } from '@/interfaces/person-search-table'

export const convertDetailsToIcon = (details: string): ControlColumnIconI => {
  switch (details) {
    case PersonControlTypeE.SharesOrVotesBeneficialOwner: {
      return {
        src: SearchIconsE.SHARES_VOTES_BENEFICIAL_OWNER,
        alt: 'Beneficial owner (e.g., through a trust)',
        tooltip: 'Beneficial owner (e.g., through a trust)',
        displayName: 'Beneficial Owner of Shares or votes'
      }
    }
    case PersonControlTypeE.SharesOrVotesIndirectControl:
    case PersonControlTypeE.SharesOrVotesInConcertControl: {
      return {
        src: SearchIconsE.SHARES_VOTES_INDIRECT_CONTROL,
        alt: 'Indirect control (e.g., through another business)',
        tooltip: 'Indirect control (e.g., through another business)',
        displayName: 'Indirect control of Shares or votes'
      }
    }
    case PersonControlTypeE.SharesOrVotesRegisteredOwner: {
      return {
        src: SearchIconsE.SHARES_VOTES_REGISTERED_OWNER,
        alt: 'Registered owner',
        tooltip: 'Registered owner',
        displayName: 'Registered owner of Shares or votes'
      }
    }
    // directors control
    case PersonControlTypeE.DirectorsDirectControl: {
      return {
        src: SearchIconsE.DIRECTORS_DIRECT_CONTROL,
        alt: 'Direct control',
        tooltip: 'Direct control',
        displayName: 'Direct control of Directors'
      }
    }
    case PersonControlTypeE.DirectorsInConcertControl: {
      return {
        src: SearchIconsE.DIRECTORS_CONTROL_MAJORITY_OF_DIRECTORS,
        alt: 'This individual has control of the majority of directors through rights and/or exercised in concert ' +
          'with other individuals',
        tooltip: 'This individual has control of the majority of directors through rights and/or exercised in ' +
          'concert with other individuals',
        displayName: 'Control of Majority of Directors'
      }
    }
    case PersonControlTypeE.DirectorsIndirectControl: {
      return {
        src: SearchIconsE.DIRECTORS_INDIRECT_CONTROL,
        alt: 'Indirect control (through another business)',
        tooltip: 'Indirect control (through another business)',
        displayName: 'Indirect Control of Directors'
      }
    }
    case PersonControlTypeE.DirectorsSignificantInfluence: {
      return {
        src: SearchIconsE.DIRECTORS_SIGNIFICANT_INFLUENCE_CONTROL,
        alt: 'Significant influence control',
        tooltip: 'Significant influence control',
        displayName: 'Indirect Control of Directors'
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
  tooltip: 'Any other reason(s) this individual is a significant individual',
  displayName: 'Other'
}
