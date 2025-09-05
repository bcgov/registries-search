export interface Address {
  addressCity: string
  addressCountry: string
  addressRegion: string
  postalCode: string
  streetAddress: string
  streetAdditional?: string
  locationDescription?: string
}

export interface EntityAddress extends Address {
  id: number
  addressType: AddressType
  deliveryInstructions: string
  streetAddressAdditional: string
}

export interface deliveryAndMailingAddress {
  deliveryAddress: Address
  mailingAddress: Address
}

export interface EntityAddressCollection {
  registeredOffice?: deliveryAndMailingAddress
  recordsOffice?: deliveryAndMailingAddress
  businessOffice?: deliveryAndMailingAddress
}
