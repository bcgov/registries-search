export interface Contact {
  email: string
  phone: string
  phoneExtension: string
}

export interface ContactsBusinessResponse {
  businessIdentifier: string
  contacts: Contact[]
  folioNumber?: string
}

export interface ContactBusinessI extends Contact {
  businessIdentifier: string
}
