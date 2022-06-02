import { StatusCodes } from 'http-status-codes'
// bc registry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local
import { useAuth } from '@/composables'
import { AuthApiProductI } from '@/interfaces/auth-api-responses'
import { axios } from '@/utils'

export async function getAccountProducts (): Promise<AuthApiProductI[]> {
  const { auth } = useAuth()
  const url = sessionStorage.getItem(SessionStorageKeys.AuthApiUrl)
  if (!url) console.error(`Error: session ${SessionStorageKeys.AuthApiUrl} expected, but not found.`)
  if (!auth.currentAccount) console.error(`Error: current account expected, but not found.`)
  const config = { baseURL: url }

  return axios.get<AuthApiProductI[]>(`orgs/${auth.currentAccount.id}/products`, config)
    .then(response => {
      const data = response?.data
      if (!data) { throw new Error('Invalid API response') }
      return data
    })
    .catch(error => {
      throw new Error('Error fetching account products, status code = ' +
        error?.response?.status?.toString() || StatusCodes.NOT_FOUND.toString(), )
    })
}

// Get SBC info from auth api /api/v1/orgs/{org_id}
export async function getSbcFromAuth (): Promise<boolean> {
  const { auth } = useAuth()
  const url = sessionStorage.getItem(SessionStorageKeys.AuthApiUrl)
  if (!url) console.error(`Error: session ${SessionStorageKeys.AuthApiUrl} expected, but not found.`)
  if (!auth.currentAccount) console.error(`Error: current account expected, but not found.`)

  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios.get(`orgs/${auth.currentAccount.id}`, config)
    .then(
      response => {
        const data = response?.data
        if (!data) return false

        const branchName = data?.branchName
        if (branchName?.includes('Service BC')) return true
        return false
      }
    ).catch(
      error => {
        throw new Error('Auth API error getting SBC: status code = ' +
                        error?.response?.status?.toString() || StatusCodes.NOT_FOUND.toString())
      }
    )
}