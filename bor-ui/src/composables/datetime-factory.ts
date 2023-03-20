import moment from 'moment'
// local
import { dateToPacificDateTimeShort } from '@/utils'

export const useDatetime = () => {
  const dateTimeString = (val: string): string => {
    return (dateToPacificDateTimeShort(new Date(val)) || 'Unknown')
  }
  const pacificDate = (date: Date) => {
    date = new Date(date.toLocaleString('en-US', { timeZone: 'America/Vancouver' }))
    return moment(date).format('MMMM D, Y')
  }
  return {
    dateTimeString,
    pacificDate
  }
}
