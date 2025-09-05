import { DateTime } from 'luxon'

export const useDatetime = () => {
  const dateTimeString = (val: string): string => {
    return (dateToPacificDateTimeShort(new Date(val)) || 'Unknown')
  }
  const pacificDate = (date: Date, format = DateTime.DATE_MED) => {
    if (!(date instanceof Date && !isNaN(date.valueOf()))) {
      return undefined
    }
    date = new Date(date.toLocaleString('en-US', { timeZone: 'America/Vancouver' }))
    return new DateTime(date).toFormat(format)
  }
  return {
    dateTimeString,
    pacificDate
  }
}
