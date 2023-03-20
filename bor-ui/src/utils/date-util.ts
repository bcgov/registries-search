import { isDate } from 'lodash'

/**
   * Converts a Date object to a date string (Month Day, Year) in Pacific timezone.
   * @param longMonth whether to show long month name (eg, December vs Dec)
   * @param showWeekday whether to show the weekday name (eg, Thursday)
   * @example "2021-01-01 07:00:00 GMT" -> "Dec 31, 2020"
   * @example "2021-01-01 08:00:00 GMT" -> "Jan 1, 2021"
   */
export function dateToPacificDate(date: Date, longMonth = false, showWeekday = false): string {
  // safety check
  if (!isDate(date) || isNaN(date.getTime())) return null

  // NB: some versions of Node have only en-US locale
  // so use that and convert results accordingly
  let dateStr = date.toLocaleDateString('en-US', {
    timeZone: 'America/Vancouver',
    weekday: showWeekday ? 'long' : undefined, // Thursday or nothing
    month: longMonth ? 'long' : 'short', // December or Dec
    day: 'numeric', // 31
    year: 'numeric' // 2020
  })

  // remove period after month
  dateStr = dateStr.replace('.', '')

  return dateStr
}

/**
 * Converts a Date object to a date and time string (Month Day, Year at HH:MM am/pm
 * Pacific time).
 * @example "2021-01-01 07:00:00 GMT" -> "Dec 31, 2020 at 11:00 pm Pacific time"
 * @example "2021-01-01 08:00:00 GMT" -> "Jan 1, 2021 at 12:00 pm Pacific time"
 */
export function dateToPacificDateTime(date: Date): string {
  // safety check
  if (!isDate(date) || isNaN(date.getTime())) return null

  const dateStr = dateToPacificDate(date, true)
  const timeStr = dateToPacificTime(date)

  return `${dateStr} at ${timeStr} Pacific time`
}

/**
 * Converts a Date object to a date and time string (Month Day, Year at HH:MM am/pm
 * Pacific time).
 * @example "2021-01-01 07:00:00 GMT" -> "Dec 31, 2020 at 11:00 pm Pacific time"
 * @example "2021-01-01 08:00:00 GMT" -> "Jan 1, 2021 at 12:00 pm Pacific time"
 */
 export function dateToPacificDateTimeShort(date: Date): string {
  // safety check
  if (!isDate(date) || isNaN(date.getTime())) return null

  const dateStr = dateToPacificDate(date, true)
  const timeStr = dateToPacificTime(date)

  return `${dateStr} at ${timeStr}`
}

/**
 * Converts a Date object to a time string (HH:MM am/pm) in Pacific timezone.
 * @example "2021-01-01 07:00:00 GMT" -> "11:00 pm"
 * @example "2021-01-01 08:00:00 GMT" -> "12:00 am"
 */
export function dateToPacificTime(date: Date): string {
  // safety check
  if (!isDate(date) || isNaN(date.getTime())) return null

  // NB: some versions of Node have only en-US locale
  // so use that and convert results accordingly
  let timeStr = date.toLocaleTimeString('en-US', {
    timeZone: 'America/Vancouver',
    hour: 'numeric', // 11
    minute: '2-digit', // 00
    hour12: true // AM/PM
  })

  // replace AM with am and PM with pm
  timeStr = timeStr.replace('AM', 'am').replace('PM', 'pm')

  return timeStr
}

/**
 * Converts an API datetime string (in UTC) to a date and time string (Month Day, Year at HH:MM am/pm
 * Pacific time).
 * @example "2021-01-01T00:00:00.000000+00:00" -> "Dec 31, 2020 at 04:00 pm Pacific time" (PST example)
 * @example "2021-07-01T00:00:00.000000+00:00" -> "Jun 30, 2021 at 05:00 pm Pacific time" (PDT example)
 */
export function apiToPacificDateTime(dateTimeString: string, longMonth = false): string {
  if (!dateTimeString) return null // safety check

  const date = apiToDate(dateTimeString)
  const dateStr = dateToPacificDate(date, longMonth)
  const timeStr = dateToPacificTime(date)

  return `${dateStr} at ${timeStr} Pacific time`
}


/**
 * Converts an API datetime string (in UTC) to a Date object.
 * @example 2021-08-05T16:56:50.783101+00:00 -> 2021-08-05T16:56:50Z
 */
export function apiToDate(dateTimeString: string): Date {
  if (!dateTimeString) return null // safety check

  // chop off the milliseconds and UTC offset and append "Zulu" timezone abbreviation
  dateTimeString = dateTimeString.slice(0, 19) + 'Z'

  return new Date(dateTimeString)
}

/**
* Converts a Date object to a date string (YYYY-MM-DD) in Pacific timezone.
* @example "2021-01-01 07:00:00 GMT" -> "2020-12-31"
* @example "2021-01-01 08:00:00 GMT" -> "2021-01-01"
*/
export function dateToYyyyMmDd(date: Date): string {
  // safety check
  if (!isDate(date) || isNaN(date.getTime())) return null

  // NB: some versions of Node have only en-US locale
  // so use that and convert results accordingly
  const dateStr = date.toLocaleDateString('en-US', {
    timeZone: 'America/Vancouver',
    month: 'numeric', // 12
    day: 'numeric', // 31
    year: 'numeric' // 2020
  })

  // convert mm/dd/yyyy to yyyy-mm-dd
  // and make sure month and day are 2 digits (eg, 03)
  const [mm, dd, yyyy] = dateStr.split('/')
  return `${yyyy}-${mm.padStart(2, '0')}-${dd.padStart(2, '0')}`
}

/** Whether the subject effective date/time is in the past. */
export function isEffectiveDatePast(effectiveDate: Date): boolean {
  return (effectiveDate <= new Date())
}

/** Whether the subject effective date/time is in the future. */
export function isEffectiveDateFuture(effectiveDate: Date): boolean {
  return (effectiveDate > new Date())
}

