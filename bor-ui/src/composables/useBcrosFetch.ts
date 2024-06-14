// following docs: https://nuxt.com/docs/guide/recipes/custom-usefetch
export function useBcrosFetch<T>(url: string, options: any) {
  return useFetch<T>(url, {
    ...options,
    watch: false,
    $fetch: useNuxtApp().$bcrosFetch
  })
}
