/* eslint-disable @typescript-eslint/no-explicit-any */
import { LDUser } from 'launchdarkly-js-client-sdk'
// BC registry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'

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

/** Gets Keycloak name from JWT. */
export function getKeycloakName(): string {
  try {
    const jwt = getJWT()
    const name = jwt.name
    if (name) return name
    throw new Error("Keycloak token is missing the 'name' attribute")
  } catch (err) {
    console.warn(err)
    throw new Error('Error getting Keycloak name')
  }
}

/** Gets Keycloak name from JWT. */
export function getKeycloakLDValues(): LDUser {
  try {
    const jwt = getJWT()

    let name = jwt.name
    if (jwt.firstname && jwt.lastname) {
      name = `${jwt.firstname.trim()} ${jwt.lastname.trim()}`
    }
    if (!jwt.idp_userid) throw new Error('No idp_userid in jwt.')
    return { key: jwt.idp_userid, name: name, custom: { 'roles': jwt.roles } }
  } catch (err) {
    console.warn(err)
    throw new Error('Error getting Keycloak LD values')
  }
}
