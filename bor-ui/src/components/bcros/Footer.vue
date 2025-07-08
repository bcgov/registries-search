<template>
  <footer
    class="flex items-center h-[56px] border-t-2 border-yellow-400 bg-bcGovColor-darkBlue text-sm"
    data-cy="bcros-footer"
  >
    <div class="h-[30.5px] w-full app-inner-container">
      <nav class="flex flex-grow">
        <ul class="p-0 -ml-2 list-none">
          <li v-for="link in links" :key="link.text" class="inline-block mr-2 pr-2 border-r last:mr-0 last:border-r-0">
            <a
              class="block py-1 px-2 text-white hover:underline"
              :href="link.href"
              :target="link.newTab ? '_blank' : '_self'"
            >
              {{ link.text }}
            </a>
          </li>
        </ul>
        <div class="flex flex-auto justify-end items-center">
          <span class="text-yellow-400 italic mr-2">{{ $t('label.footer.version') }}</span>
          <UTooltip
            :text="aboutText"
            :popper="{
              placement: 'top',
              arrow: true
            }"
          >
            <div class="icon-container mt-1" role="img" aria-label="information">
              <UIcon class="text-2xl text-white" name="i-mdi-information-outline" />
            </div>
          </UTooltip>
        </div>
      </nav>
    </div>
  </footer>
</template>

<script setup lang="ts">
const aboutText = useRuntimeConfig().public.appNameDisplay +
  ` v${useRuntimeConfig().public.version}`

const links = [
  { text: 'Home', href: '/', newTab: false },
  { text: 'Release Notes', href: 'https://www.release-notes.bcregistry.gov.bc.ca', newTab: true },
  { text: 'Disclaimer', href: 'https://www2.gov.bc.ca/gov/content/home/disclaimer', newTab: true },
  { text: 'Privacy', href: 'https://www2.gov.bc.ca/gov/content/home/privacy', newTab: true },
  { text: 'Accessibility', href: 'https://www2.gov.bc.ca/gov/content/home/accessibility', newTab: true },
  { text: 'Copyright', href: 'https://www2.gov.bc.ca/gov/content/home/copyright', newTab: true }
]
</script>
