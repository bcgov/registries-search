export function formatAddress(address: Address | undefined): ConnectAddress {
  return {
    street: address?.streetAddress ?? '',
    streetAdditional: address?.streetAdditional ?? '',
    city: address?.addressCity ?? '',
    region: address?.addressRegion ?? '',
    postalCode: address?.postalCode ?? '',
    country: address?.addressCountry ?? '',
    locationDescription: address?.locationDescription ?? ''
  }
}
