export interface ContactI {
  email: string
  phone: string
  phoneExtension: string
}

export interface ContactsBusinessResponseI {
  businessIdentifier: string
  contacts: ContactI[],
  folioNumber?: string
}

export interface ContactBusinessI extends ContactI {
  businessIdentifier: string
}
