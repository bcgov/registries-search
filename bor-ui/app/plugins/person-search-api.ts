export default defineNuxtPlugin((nuxtApp) => {
  const rtc = nuxtApp.$config.public
  const apiUrl = rtc.borApiUrl + rtc.borApiVersion
  const appName = rtc.appName
  const xApiKey = rtc.borApiKey

  const api = $fetch.create({
    baseURL: apiUrl,
    async onRequest({ options }) {
      const auth = useConnectAuth()
      const accountStore = useConnectAccountStore()

      const token = await auth.getToken()
      const accountId = accountStore.currentAccount.id

      options.headers.set('Authorization', `Bearer ${token}`)
      options.headers.set('App-Name', appName)
      options.headers.set('X-Apikey', xApiKey)
      options.headers.set('Account-Id', String(accountId))
    }
  })

  return {
    provide: {
      personSearchApi: api
    }
  }
})
