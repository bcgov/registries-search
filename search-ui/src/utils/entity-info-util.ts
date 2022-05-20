import {
    EffectOfOrderTypes,
    FilingNames,
    FilingStatus,
    FilingTypes
} from '@/enums'
import {
    GetCorpFullDescription,
    GetCorpInfoObject,
    GetCorpNumberedDescription
} from '@bcrs-shared-components/corp-type-module'


/** Returns True if item status is Cancelled. */
export const isStatusCancelled = (item: any): boolean => {
    return (item.status === FilingStatus.CANCELLED)
}

/** Returns True if item status is Completed. */
export const isStatusCompleted = (item: any): boolean => {
    return (item.status === FilingStatus.COMPLETED)
}

/** Returns True if item status is Corrected. */
export const isStatusCorrected = (item: any): boolean => {
    return (item.status === FilingStatus.CORRECTED)
}

/** Returns True if item status is Deleted. */
export const isStatusDeleted = (item: any): boolean => {
    return (item.status === FilingStatus.DELETED)
}

/** Returns True if item status is Draft. */
export const isStatusDraft = (item: any): boolean => {
    return (item.status === FilingStatus.DRAFT)
}

/** Returns True if item status is Error. */
export const isStatusError = (item: any): boolean => {
    return (item.status === FilingStatus.ERROR)
}

/** Returns True if item status is New. */
export const isStatusNew = (item: any): boolean => {
    return (item.status === FilingStatus.NEW)
}

/** Returns True if item status is Paid. */
export const isStatusPaid = (item: any): boolean => {
    return (item.status === FilingStatus.PAID)
}

/** Returns True if item status is Pending. */
export const isStatusPending = (item: any): boolean => {
    return (item.status === FilingStatus.PENDING)
}

/** Returns True if item status is Withdrawn. */
export const isStatusWithdrawn = (item: any): boolean => {
    return (item.status === FilingStatus.WITHDRAWN)
}

//
// Filing Type helpers
//

/** Returns True if filing is an Alteration. */
export const isTypeAlteration = (item: any): boolean => {
    return (item.name === FilingTypes.ALTERATION)
}

/** Returns True if filing is an Annual Report. */
export const isTypeAnnualReport = (item: any): boolean => {
    return (item.name === FilingTypes.ANNUAL_REPORT)
}

/** Returns True if filing is a Change of Address. */
export const isTypeChangeOfAddress = (item: any): boolean => {
    return (item.name === FilingTypes.CHANGE_OF_ADDRESS)
}

/** Returns True if filing is a Change of Directors. */
export const isTypeChangeOfDirectors = (item: any): boolean => {
    return (item.name === FilingTypes.CHANGE_OF_DIRECTORS)
}

/** Returns True if filing is a Change of Name. */
export const isTypeChangeOfName = (item: any): boolean => {
    return (item.name === FilingTypes.CHANGE_OF_NAME)
}

/** Returns True if filing is a Correction. */
export const isTypeCorrection = (item: any): boolean => {
    return (item.name === FilingTypes.CORRECTION)
}

/** Returns True if filing is a Dissolution. */
export const isTypeDissolution = (item: any): boolean => {
    return (item.name === FilingTypes.DISSOLUTION)
}

/** Returns True if filing is an Incorporation Application. */
export const isTypeIncorporationApplication = (item: any): boolean => {
    return (item.name === FilingTypes.INCORPORATION_APPLICATION)
}

/** Returns True if filing is a Registration Application. */
export const isTypeRegistrationApplication = (item: any): boolean => {
    return (item.name === FilingTypes.REGISTRATION)
}

/** Returns True if filing is a Transition. */
export const isTypeTransition = (item: any): boolean => {
    return (item.name === FilingTypes.TRANSITION)
}

/** Returns True if filing is a Staff Only filing. */
export const isTypeStaff = (item: any): boolean => {
    return [
        FilingTypes.REGISTRARS_NOTATION,
        FilingTypes.REGISTRARS_ORDER,
        FilingTypes.COURT_ORDER
    ].includes(item.name)
}

//
// Effect of Order helpers
//
/** Returns True if effect of order is Plan of Arrangement. */
export const isEffectOfOrderPlanOfArrangement = (effectOfOrder: EffectOfOrderTypes): boolean => {
    return (effectOfOrder === EffectOfOrderTypes.PLAN_OF_ARRANGEMENT)
}

//
// Conversion helpers
//

// from external module
export const getCorpTypeInfo = GetCorpInfoObject
export const getCorpTypeDescription = GetCorpFullDescription
export const getCorpTypeNumberedDescription = GetCorpNumberedDescription

/**
 * Converts the filing type to a filing name.
 * @param type the filing type to convert
 * @param agmYear the AGM Year to be appended to the filing name (optional)
 * @param alterationRequired A boolean indicating a required business type change
 * @returns the filing name
 */
 export const filingTypeToName = (type: FilingTypes, agmYear: string = null, alterationRequired = false): string => {
    if (!type) return 'Unknown Type' // safety check
    switch (type) {
        case FilingTypes.ALTERATION:
            return alterationRequired ? FilingNames.ALTERATION : FilingNames.CHANGE_OF_COMPANY_INFO
        case FilingTypes.ANNUAL_REPORT: return FilingNames.ANNUAL_REPORT + (agmYear ? ` (${agmYear})` : '')
        case FilingTypes.CHANGE_OF_ADDRESS: return FilingNames.CHANGE_OF_ADDRESS
        case FilingTypes.CHANGE_OF_DIRECTORS: return FilingNames.CHANGE_OF_DIRECTORS
        case FilingTypes.CHANGE_OF_NAME: return FilingNames.CHANGE_OF_NAME
        case FilingTypes.CONVERSION: return FilingNames.CONVERSION
        case FilingTypes.CORRECTION: return FilingNames.CORRECTION
        case FilingTypes.COURT_ORDER: return FilingNames.COURT_ORDER
        case FilingTypes.DISSOLUTION: return FilingNames.DISSOLUTION
        case FilingTypes.DISSOLVED: return FilingNames.DISSOLVED
        case FilingTypes.INCORPORATION_APPLICATION: return FilingNames.INCORPORATION_APPLICATION
        case FilingTypes.INVOLUNTARY_DISSOLUTION: return FilingNames.INVOLUNTARY_DISSOLUTION
        case FilingTypes.REGISTRARS_NOTATION: return FilingNames.REGISTRARS_NOTATION
        case FilingTypes.REGISTRARS_ORDER: return FilingNames.REGISTRARS_ORDER
        case FilingTypes.SPECIAL_RESOLUTION: return FilingNames.SPECIAL_RESOLUTION
        case FilingTypes.TRANSITION: return FilingNames.TRANSITION_APPLICATION
        case FilingTypes.VOLUNTARY_DISSOLUTION: return FilingNames.VOLUNTARY_DISSOLUTION
        case FilingTypes.REGISTRATION: return FilingNames.REGISTRATION
    }
    // fallback for unknown filings
    return camelCaseToWords(type)
}

/**
 * Converts a string in "camelCase" (or "PascalCase") to separate, title-case words,
 * suitable for a title or proper name.
 * @param s the string to convert
 * @returns the converted string
 */
 export const camelCaseToWords = (s: string): string => {
    return s?.split(/(?=[A-Z])/).join(' ').replace(/^\w/, c => c.toUpperCase()) || ''
}
