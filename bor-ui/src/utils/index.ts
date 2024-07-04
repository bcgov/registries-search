export * from './error-dialog-options'
export * from './table'

/** Capitalize the first letter of the first word of the string. */
export const capFirstLetter = (val: string) => val.charAt(0).toUpperCase() + val.toLocaleLowerCase().slice(1)

/** Capitalize the first letter of each word in the string. */
export const capFirstLetterAll = (val: string) => val.split(' ').map(capFirstLetter).join(' ')
