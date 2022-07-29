/* eslint-disable @typescript-eslint/no-explicit-any */
// BC registry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local
import { StaffRoles, UserRoles } from '@/enums'

/** Gets Keycloak JWT and parses it. */
function getJWT(): any {
  const token = sessionStorage.getItem(SessionStorageKeys.KeyCloakToken)
  if (token) {
    return parseToken(token)
  }
  throw new Error('Error getting Keycloak token')
}

/** Decodes and parses Keycloak token. */
function parseToken(token: string): any {
  try {
    const base64Url = token.split('.')[1]
    const base64 = decodeURIComponent(
      window
        .atob(base64Url)
        .split('')
        .map(function (c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
        })
        .join('')
    )
    return JSON.parse(base64)
  } catch (err) {
    throw new Error('Error parsing Keycloak token - ' + err)
  }
}

/** Gets Keycloak roles from JWT. */
export function getKeycloakRoles(): Array<StaffRoles | UserRoles> {
  const jwt = getJWT()
  const keycloakRoles = jwt.roles
  if (keycloakRoles && keycloakRoles.length > 0) {
    return keycloakRoles
  }
  throw new Error('Error getting Keycloak roles')
}

/** Gets Keycloak name from JWT. */
export function getKeycloakName(): string {
  const jwt = getJWT()
  const name = jwt.name
  if (name) return name
  throw new Error('Error getting Keycloak name')
}
