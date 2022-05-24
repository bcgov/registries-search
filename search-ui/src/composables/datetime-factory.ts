import moment from 'moment'

export const useDatetime = () => {
  const pacificDate = (date: Date) => {
    date = new Date(date.toLocaleString('en-US', { timeZone: 'America/Vancouver' }))
    return moment(date).format('MMMM D, Y')
  }
  return {
    pacificDate
  }
}
