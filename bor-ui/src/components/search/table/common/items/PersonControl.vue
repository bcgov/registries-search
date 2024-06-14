<template>
  <div class="space-y-2">
    <BaseDetailsInfoBox
      v-for="control in controls"
      :key="control.title"
      :title="control.title"
      :data-cy="`control-${control.title.replaceAll(' ', '')}`"
    >
      <template #content>
        <div>
          <!-- icons -->
          <div v-if="control.icons" class="flex space-x-1" data-cy="control-icons-container">
            <UTooltip
              v-for="icon in control.icons"
              :key="icon.src"
              :text="icon.tooltip"
              :popper="{ placement: 'top' }"
              location="top"
            >
              <img :src="icon.src" :alt="icon.alt">
            </UTooltip>
          </div>
          <!-- text -->
          <div v-if="control.content">
            <p data-cy="controls-content">
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
              wrapper: 'divide-none space-y-1',
              default: { class: 'py-1 bg-transparent text-primary-500 font-normal' }
            }"
            data-cy="controls-accordion"
          >
            <template #default="{ item, open }">
              <UButton color="primary" :label="item.label" variant="link" :data-cy="`controls-accordian-${item.type}`">
                <template #leading>
                  <UIcon
                    name="i-heroicons-chevron-down-20-solid"
                    class="w-5 h-5 transform transition-transform duration-200"
                    :class="[open && 'rotate-180']"
                  />
                </template>
              </UButton>
            </template>
            <template #item="{ item }">
              <div class="flex flex-col text-sm text-gray-700">
                <span v-for="name in item.content" :key="name">
                  {{ name }}
                </span>
              </div>
            </template>
          </UAccordion>
        </div>
      </template>
    </BaseDetailsInfoBox>
    <BaseDetailsInfoBox
      v-if="!!otherControl"
      title="Other"
      :content="otherControl"
      data-cy="control-Other"
    />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ role: SearchResultRoleI }>()

const controls: Ref<ControlColumnDetailsInfoBoxI[]> = ref([])
const otherControl: Ref<string | undefined> = ref(undefined)

const t = useNuxtApp().$i18n.t

const getAccordianObjs = (control: ControlColumnDetailsInfoBoxI) => {
  const accordianObjs = []
  if (control.inConcertNames) {
    accordianObjs.push({
      type: 'inConcert',
      label: t('label.control.inConcert') + ` (${control.inConcertNames.length})`,
      content: control.inConcertNames
    })
  }
  if (control.actingJointlyNames) {
    accordianObjs.push({
      type: 'jointly',
      label: t('label.control.actingJointly') + ` (${control.actingJointlyNames.length})`,
      content: control.actingJointlyNames
    })
  }
  return accordianObjs
}

const getContentText = (interest: SearchResultRoleInterestI) => {
  if (interest.sharesExact) {
    return `${interest.sharesExact}%`
  }
  return t('text.control.percentage', { min: interest.sharesMin || 0, max: interest.sharesMax || 100 })
}

const getUpdatedControl = (
  interest: SearchResultRoleInterestI,
  control: ControlColumnDetailsInfoBoxI,
  title: string,
  icon: ControlColumnIconI
) => {
  // init control option
  if (!control) {
    const contentTypes = [PersonControlCategoryE.SHARES, PersonControlCategoryE.VOTES]
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
  const shareControls: Ref<ControlColumnDetailsInfoBoxI> = ref(undefined)
  const voteControls: Ref<ControlColumnDetailsInfoBoxI> = ref(undefined)
  const directorControls: Ref<ControlColumnDetailsInfoBoxI> = ref(undefined)

  // sort is so that the icons are always displayed in the same order
  const interests = props.role.relatedInterests || []
  for (const interest of interests.sort((a, b) => a.details?.localeCompare(b.details))) {
    // skip older records (only showing most current info)
    if (interest.endDate) { continue }

    const icon = convertDetailsToIcon(interest.details)

    switch (interest.interestType) {
      case PersonControlCategoryE.DIRECTORS:
        directorControls.value = getUpdatedControl(interest, directorControls.value, t('label.control.directors'), icon)
        break
      case PersonControlCategoryE.OTHER:
        otherControl.value = interest.otherReason
        break
      case PersonControlCategoryE.SHARES:
        shareControls.value = getUpdatedControl(interest, shareControls.value, t('label.control.shares'), icon)
        break
      case PersonControlCategoryE.VOTES:
        voteControls.value = getUpdatedControl(interest, voteControls.value, t('label.control.votes'), icon)
        break
      default:
        continue
    }
  }
  // update the controls with combined share/vote/director interest controls
  controls.value = [shareControls.value, voteControls.value, directorControls.value].filter(val => !!val)
})
</script>
