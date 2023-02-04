<template>
  <div id="breadcrumb">
    <v-container class="container py-0">
      <v-row no-gutters>
        <v-col cols="auto">
          <v-btn
            id="breadcrumb-back-btn"
            class="back-btn"
            exact
            icon small
            :disabled="breadcrumbs?.length <= 1"
            @click="back()"
          >
            <v-icon color="primary">mdi-arrow-left</v-icon>
          </v-btn>
        </v-col>

        <v-divider class="mx-3" color="white" vertical />

        <v-col class="breadcrumb-col col col-auto">
          <div v-for="crumb, index in breadcrumbs" :key="crumb.text" class="v-breadcrumb-item">
            <span
              class="breadcrumb-text"
              :class="isLast(index) ? 'inactive-crumb' : 'active-crumb'"
              @click="navigate(crumb)"
            >
                {{ crumb.text }}
            </span>
            <v-icon icon="mdi-chevron-right" v-if="breadcrumbs?.length > 1 && isLast(index) == false" />
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
// External
import { PropType } from 'vue'
import { useRouter } from 'vue-router'
import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'

const props = defineProps({
  breadcrumbs: { type: Array as PropType<BreadcrumbIF[]> }
})

const router = useRouter()

const back = () => {
  const crumbsLength = props.breadcrumbs.length
  const backCrumb = props.breadcrumbs[crumbsLength - 2]
  navigate(backCrumb)
}

const isLast = (index: number): boolean =>  {
  return index === props.breadcrumbs.length - 1;
}

const navigate = (breadcrumb: BreadcrumbIF): void => {
  if (breadcrumb.to) {
    router.push(breadcrumb.to)
  } else if (breadcrumb.href) {
    window.location.assign(breadcrumb.href)
  }
}

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#breadcrumb {
  height: 45px;
  background-color: $app-dk-blue;
  color: white;
  display: flex;
  align-items: center;
  li {
    margin-bottom: 0 !important;
  }
}
.back-btn {
  background-color: white;
  color: $app-dk-blue;
}
.v-breadcrumbs li {
    align-items: center;
    display: inline-flex;
    font-size: 14px;
}
.breadcrumb-text {
  font-size: 0.8125rem !important;
  color: white;
}
.breadcrumb-col {
  display: flex;
  align-items: center;
}
.active-crumb {
  text-decoration: underline !important;
  cursor: pointer !important;
}
.inactive-crumb {
  cursor: default !important; // To override default or local link styling
}
.text-primary{
  color: #1669bb!important;
}

@media(min-width:960px) {
	.container {
		max-width: 900px
	}
}

@media(min-width:1264px) {
	.container {
		max-width: 1185px
	}
}

@media(min-width:1904px) {
	.container {
		max-width: 1785px
	}
}

.container {
    max-width: 1360px;
}

:deep(.v-breadcrumbs .v-breadcrumbs__divider) {
  color: white !important;
  margin-bottom: 0;
}
:deep(.theme--bcgov.v-btn.v-btn--disabled) {
  opacity: .4;
  .v-icon {
    color: $app-blue !important;
  }
}
:deep(.v-btn--icon.v-btn--density-default) {
  height: 28px;
  width: 28px;
}
</style>