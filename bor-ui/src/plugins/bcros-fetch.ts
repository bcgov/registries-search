// custom fetch docs: https://nuxt.com/docs/guide/recipes/custom-usefetch

const addHeader = (headers: HeadersInit, key: string, value: string) => {
  if (Array.isArray(headers)) {
    headers.push([key, value])
  } else if (headers instanceof Headers) {
    headers.set(key, value)
  } else {
    headers[key] = value
  }
}

const headerExists = (headers: HeadersInit, key: string) => {
  if (Array.isArray(headers)) {
    return !!headers.find(val => val[0] === key)
  }
  return Object.keys(headers).includes(key)
}

export default defineNuxtPlugin(() => {
  const bcrosFetch = $fetch.create({
    onRequest({ options }) {
      const headers = options.headers ||= {}

      if (!headerExists(headers, 'Authorization') && useBcrosKeycloak().kc?.token) {
        addHeader(headers, 'Authorization', `Bearer ${useBcrosKeycloak().kc.token}`)
      }

      if (!headerExists(headers, 'Account-Id') && useBcrosAccount().currentAccount?.id) {
        addHeader(headers, 'Account-Id', (useBcrosAccount().currentAccount.id).toString())
      }

      if (!headerExists(headers, 'Accept')) {
        addHeader(headers, 'Accept', 'application/json')
      }
    }
  })

  // Expose to useNuxtApp().$bcrosFetch
  return {
    provide: {
      bcrosFetch
    }
  }
})
