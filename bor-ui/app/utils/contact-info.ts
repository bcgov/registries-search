const contactInfo = {
  helpDesk: [
    {
      type: 'phone',
      href: 'tel:+1-800-663-6102',
      title: 'Canada and U.S. Toll Free:',
      value: '1-800-663-6102'
    },
    {
      type: 'email',
      href: 'mailto:BCOLHelp@gov.bc.ca',
      title: 'Email:',
      value: 'BCOLHelp@gov.bc.ca'
    }
  ] as ConnectContactItem[],
  registries: [
    {
      type: 'phone',
      href: 'tel:+1-877-526-1526',
      title: 'Canada and U.S. Toll Free:',
      value: '1-877-526-1526'
    },
    {
      type: 'phone',
      href: 'tel:+1-250-387-7848',
      title: 'Victoria Office:',
      value: '250-387-7848'
    },
    {
      type: 'email',
      href: 'mailto:BCRegistries@gov.bc.ca',
      title: 'Email:',
      value: 'BCRegistries@gov.bc.ca'
    }
  ] as ConnectContactItem[]
}

export const getContactInfo = (group: 'helpDesk' | 'registries'): ConnectContactItem[] => {
  return contactInfo[group]
}
