export const getChildHeaderWidth = (
  headers: BaseTableHeaderI[],
  headerValue: string,
  childHeaders: string[]
): string => {
  try {
    // get the total width percentage of the parent container
    const totalPercentage = headers.reduce((total, curHeader) => {
      if (childHeaders.find(val => val === curHeader.value)) {
        return total + parseFloat(curHeader.width.replace('%', ''))
      } else {
        return total
      }
    }, 0)

    // prevent getting 'Infinity%'
    if (totalPercentage === 0) {
      console.error('total width percentage is zero')
      return '0%'
    }

    // get the header
    const header = headers.find(val => val.value === headerValue)
    if (!header) {
      return '0%'
    }

    const widthPercentage = parseFloat(header.width.replace('%', '')) / totalPercentage

    return `${widthPercentage * 100}%`
  } catch (error) {
    // handle potential errors such as invalid header.width string
    console.error(error)
    return '0%'
  }
}
