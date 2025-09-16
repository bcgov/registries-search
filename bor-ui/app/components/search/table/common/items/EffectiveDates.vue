<script setup lang="ts">
const prop = defineProps<{ role: SearchResultRole }>()

const getEffectiveDates = (role: SearchResultRole) => {
  const effectiveDates = []

  for (const startEndDates of role.roleDates) {
    const start = startEndDates.start ? startEndDates.start.substring(0, 10) : undefined
    const end = startEndDates.end ? startEndDates.end.substring(0, 10) : undefined
    let dateRange = ''
    if (role.roleType === SearchRoleType.INCORPORATOR) {
      dateRange += start
    } else {
      dateRange += `${start || 'Unknown'} To ${end || 'Current'}`
    }

    effectiveDates.push({ start, dateRange })
  }

  // sort effectiveDates by start date
  effectiveDates.sort((a, b) => {
    if (a.start && b.start) {
      return b.start.localeCompare(a.start)
    }
    return -1
  })
  return effectiveDates
}

const effectiveDates = ref(getEffectiveDates(prop.role))
</script>

<template>
  <div class="dates pr-2">
    <div
      v-for="(effectiveDate, index) in effectiveDates"
      :key="index"
      class="text-right"
    >
      {{ effectiveDate.dateRange }}
    </div>
  </div>
</template>

<style scoped>
.dates > div:not(:first-child) {
  margin-top: 8px;
}
</style>
