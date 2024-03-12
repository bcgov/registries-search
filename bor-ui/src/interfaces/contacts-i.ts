export interface ContactI {
  email: string
  phone: string
  phoneExtension: string
}

export interface ContactsBusinessResponseI {
  businessIdentifier: string
  contacts: ContactI[]
}

export interface ContactBusinessI extends ContactI {
  businessIdentifier: string
}
