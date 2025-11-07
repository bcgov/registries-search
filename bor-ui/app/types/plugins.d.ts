// plugin types not being inferred
// https://nuxt.com/docs/4.x/guide/directory-structure/app/plugins#typing-plugins

import type { $Fetch } from 'ofetch'

declare module '#app' {
  interface NuxtApp {
    $businessApi: $Fetch
    $personSearchApi: $Fetch
  }
}
export {}
