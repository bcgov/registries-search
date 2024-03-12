import moment from 'moment'

export const useDatetime = () => {
  const dateTimeString = (val: string): string => {
    return (dateToPacificDateTimeShort(new Date(val)) || 'Unknown')
  }
  const pacificDate = (date: Date, format = 'MMMM D, Y') => {
    date = new Date(date.toLocaleString('en-US', { timeZone: 'America/Vancouver' }))
    return moment(date).format(format)
  }
  return {
    dateTimeString,
    pacificDate
  }
}
