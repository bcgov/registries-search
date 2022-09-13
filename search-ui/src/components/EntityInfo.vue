<template>
  <div id="entity-info">
    <v-container class="container justify-center py-0">
      <v-row no-gutters>
        <v-col cols="9">
          <header>
            <!-- Entity Name -->
            <div id="entity-legal-name" aria-label="Business Legal Name">
              <span>{{ name }}</span>
            </div>
            <!-- Description -->
            <div id="business-subtitle">{{ businessDescription || 'Description Unavailable' }}</div>
          </header>

          <menu>
            <span v-if="isHistorical">
              <v-chip id="historical-chip" small label>
                <strong>HISTORICAL</strong>
              </v-chip>
              <!-- <span class="mx-3" style="font-size: 0.875rem;">{{ historicalReason }}</span> -->
            </span>
          </menu>
        </v-col>

        <v-col cols="3" class="pl-5">
          <dl>
            <template v-for="info in businessInfo" :key="info.term">
              <dt class="mr-2">{{ info.term }}:</dt>
              <dd>{{ info.value }}</dd>
            </template>
          </dl>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
// local
import { useDatetime, useEntity } from '@/composables'
import { BusinessStatuses, CorpTypeCd } from '@/enums'

// composables
const { pacificDate } = useDatetime()
const { entity, entityNumberLabel, getEntityDescription } = useEntity()
// computed
const businessDescription = computed(() => getEntityDescription(entity.legalType as CorpTypeCd))
const incorpDate = computed(() => pacificDate(new Date(entity.incorporationDate)))
const businessInfo = computed(() => [
  { term: 'Incorporation Date', value: incorpDate.value || 'Not Available' },
  { term: entityNumberLabel.value, value: entity.identifier || 'Not Available' },
  { term: 'Business Number', value: entity.bn || 'Not Available'},
])
const isHistorical = computed(() => entity.status === BusinessStatuses.HISTORICAL)
const name = computed(() => entity.name?.toUpperCase() || 'Name Unavailable')
</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#entity-info {
  background: $BCgovInputBG;
  padding: 30px 0px;
  transition: all 1s;
  .v-chip--label {
    font-size: 0.625rem !important;
    letter-spacing: 0.5px;
  }
}
#entity-legal-name,
#incorp-app-title {
  display: inline-block;
  color: $gray9;
  letter-spacing: -0.01rem;
  font-size: 1.375rem;
  font-weight: 700;
  text-transform: uppercase;
}
#entity-status {
  margin-top: 5px;
  margin-left: 0.5rem;
  vertical-align: top;
}
#business-subtitle {
  font-size: 0.875rem;
  color: $gray7;
}
#historical-chip {
  background-color: $primary-blue;
  color: white;
  height: 19px;
  font-size: 10px;
}
// vertical lines between buttons:
menu > span + span {
  border-left: 1px solid $gray3;
  border-radius: 0;
}
dl {
  font-size: 0.875rem;
  line-height: 1.5rem;
}
dt {
  color: $gray9;
  font-weight: bold;
  float: left;
  clear: left;
  margin-right: 0.5rem;
}
.pending-alert .v-icon {
  font-size: 18px; // same as other v-icons
  padding-left: 0.875rem;
}
</style>