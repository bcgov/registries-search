const contactInfo = {
  helpDesk: [
    {
      icon: 'i-mdi-phone',
      href: 'tel:+1-800-663-6102',
      label: 'Canada and U.S. Toll Free',
      value: '1-800-663-6102'
    },
    {
      icon: 'i-mdi-email',
      href: 'mailto:BCOLHelp@gov.bc.ca',
      label: 'Email',
      value: 'BCOLHelp@gov.bc.ca'
    }
  ],
  registries: [
    {
      icon: 'i-mdi-phone',
      href: 'tel:+1-877-526-1526',
      label: 'Canada and U.S. Toll Free',
      value: '1-877-526-1526'
    },
    {
      icon: 'i-mdi-phone',
      href: 'tel:+1-250-387-7848',
      label: 'Victoria Office',
      value: '250-387-7848'
    },
    {
      icon: 'i-mdi-email',
      href: 'mailto:BCRegistries@gov.bc.ca',
      label: 'Email',
      value: 'BCRegistries@gov.bc.ca'
    }
  ]
}

export const getContactInfo = (group: 'helpDesk' | 'registries'): ContactInfoI[] => {
  return contactInfo[group]
}
