<script setup lang="ts">
const props = defineProps<{ role: SearchResultRole }>()

const controls: Ref<ControlColumnDetailsInfoBox[]> = ref([])
const otherControl: Ref<string | undefined> = ref(undefined)

const t = useNuxtApp().$i18n.t

const getAccordianObjs = (control: ControlColumnDetailsInfoBox) => {
  const accordianObjs = []
  if (control.inConcertNames) {
    accordianObjs.push({
      type: 'inConcert',
      label: t('label.actingInConcert') + ` (${control.inConcertNames.length})`,
      content: control.inConcertNames
    })
  }
  if (control.actingJointlyNames) {
    accordianObjs.push({
      type: 'jointly',
      label: t('label.actingJointly') + ` (${control.actingJointlyNames.length})`,
      content: control.actingJointlyNames
    })
  }
  return accordianObjs
}

const getContentText = (interest: SearchResultRoleInterest) => {
  if (interest.sharesExact) {
    return `${interest.sharesExact}%`
  }
  return t('text.control.percentage', { min: interest.sharesMin || 0, max: interest.sharesMax || 100 })
}

const getUpdatedControl = (
  interest: SearchResultRoleInterest,
  control: ControlColumnDetailsInfoBox | undefined,
  title: string,
  icon: ControlColumnIcon | undefined
) => {
  // init control option
  if (!control) {
    const contentTypes = [PersonControlCategory.SHARES, PersonControlCategory.VOTES]
    const content = contentTypes.includes(interest.interestType) ? getContentText(interest) : undefined
    control = { title, content, icons: [] }
  }
  // if icon and not a duplicate icon, then add it to icon list
  if (icon && !control.icons?.find(val => val.src === icon.src)) {
    control.icons.push(icon)
  }
  // if parties, then add their names to applicable control name list
  if (interest.relatedParties) {
    if (interest.details.includes('actingJointly')) {
      control.actingJointlyNames = interest.relatedParties.map(val => val.interestPartyName).filter(val => !!val)
    } else if (interest.details.includes('inConcertControl')) {
      control.inConcertNames = interest.relatedParties.map(val => val.interestPartyName).filter(val => !!val)
    }
  }
  return control
}

onMounted(() => {
  const shareControls: Ref<ControlColumnDetailsInfoBox | undefined> = ref(undefined)
  const voteControls: Ref<ControlColumnDetailsInfoBox | undefined> = ref(undefined)
  const directorControls: Ref<ControlColumnDetailsInfoBox | undefined> = ref(undefined)

  // sort is so that the icons are always displayed in the same order
  const interests = props.role.relatedInterests || []
  for (const interest of interests.sort((a: any, b: any) => a.details?.localeCompare(b.details))) {
    // skip older records (only showing most current info)
    if (interest.endDate) {
      continue
    }

    const icon = convertDetailsToIcon(interest.details)

    switch (interest.interestType) {
      case PersonControlCategory.DIRECTORS:
        directorControls.value = getUpdatedControl(interest, directorControls.value, t('label.directors'), icon)
        break
      case PersonControlCategory.OTHER:
        otherControl.value = interest.otherReason
        break
      case PersonControlCategory.SHARES:
        shareControls.value = getUpdatedControl(interest, shareControls.value, t('label.shares'), icon)
        break
      case PersonControlCategory.VOTES:
        voteControls.value = getUpdatedControl(interest, voteControls.value, t('label.votes'), icon)
        break
      default:
        continue
    }
  }
  // update the controls with combined share/vote/director interest controls
  controls.value = [shareControls.value, voteControls.value, directorControls.value].filter(val => !!val)
})
</script>

<template>
  <div class="space-y-2">
    <DetailsInfoBox
      v-for="control in controls"
      :key="control.title"
      :title="control.title"
      :data-testid="`control-${control.title.replaceAll(' ', '')}`"
    >
      <template #content>
        <div>
          <!-- icons -->
          <div
            v-if="control.icons"
            class="flex space-x-1"
            data-testid="control-icons-container"
          >
            <UTooltip
              v-for="icon in control.icons"
              :key="icon.src"
              arrow
              :content="{
                align: 'center',
                side: 'top',
              }"
              :delay-duration="0"
              :text="icon.tooltip"
            >
              <img :src="icon.src" :alt="icon.alt">
            </UTooltip>
          </div>
          <!-- text -->
          <div v-if="control.content">
            <p data-testid="controls-content">
              {{ control.content }}
            </p>
          </div>
          <!-- connected individuals -->
          <UAccordion
            v-if="!!getAccordianObjs(control)"
            class="mt-1"
            :items="getAccordianObjs(control)"
            multiple
            :ui="{
              item: 'border-none',
              trigger: 'p-0 py-1 bg-transparent text-primary font-normal',
              trailingIcon: 'hidden',
            }"
            data-testid="controls-accordion"
          >
            <template #default="{ item, open }">
              <UButton
                color="primary"
                class="p-0"
                :label="item.label"
                variant="link"
                :data-testid="`controls-accordion-${item.type}`"
              >
                <template #leading>
                  <UIcon
                    name="i-heroicons-chevron-down-20-solid"
                    class="w-5 h-5 transform transition-transform duration-200"
                    :class="[open && 'rotate-180']"
                  />
                </template>
              </UButton>
            </template>
            <template #content="{ item }">
              <div class="ml-[30px] mb-3 flex flex-col text-sm text-neutral">
                <span v-for="name in item.content" :key="name">
                  {{ name }}
                </span>
              </div>
            </template>
          </UAccordion>
        </div>
      </template>
    </DetailsInfoBox>
    <DetailsInfoBox
      v-if="!!otherControl"
      title="Other"
      :content="otherControl"
      data-testid="control-Other"
    />
  </div>
</template>
