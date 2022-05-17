<template>
  <div id="breadcrumb">
    <div class="container">
      <v-row no-gutters>
        <v-col cols="auto">
          <v-btn
            id="breadcrumb-back-btn"
            class="back-btn"
            exact
            :href="backUrl()"
            icon small
            :disabled="breadcrumbs?.length <= 1"
          >
            <v-icon color="primary">mdi-arrow-left</v-icon>
          </v-btn>
        </v-col>

        <v-divider class="mx-3" color="white" vertical />

        <div class="breadcrumb-col col col-auto">
          <ul class="v-breadcrumbs pa-0 ma-0 theme--light">
            <li v-for="(crumb, ci) in breadcrumbs" :key="ci">
              <div class="v-breadcrumb-item">
                <span class="breadcrumb-text" :class="isLast(ci) ? 'inactive-crumb' : 'active-crumb'">
                   {{ crumb.text }}
                </span>
              </div>
              <v-icon icon="mdi-chevron-right" v-if="breadcrumbs?.length > 1 && isLast(ci) == false"></v-icon>
            </li>
          </ul>
        </div>
      </v-row>
    </div>
  </div>
</template>

<script setup lang="ts">
// External
import { PropType } from 'vue'
import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'

const props = defineProps({
  breadcrumbs: { type: Array as PropType<BreadcrumbIF[]> }
})

const backUrl = (): string =>  {
  const crumbsLength = props.breadcrumbs.length
  return props.breadcrumbs[crumbsLength - 2]?.href || ''
}

const isLast = (index): boolean =>  {
  return index === props.breadcrumbs.length - 1;
}

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#breadcrumb {
  max-height: 45px;
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

.container {
	width: 100%;
	padding: 12px;
	margin-right: auto;
	margin-left: auto
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

::v-deep {
  .v-breadcrumbs .v-breadcrumbs__divider {
    color: white !important;
    margin-bottom: 0;
  }
  .theme--light.v-btn.v-btn--disabled {
    opacity: .4;
    .v-icon {
      color: $app-blue !important;
    }
  }
  .v-btn--icon.v-btn--density-default {
    height: 28px;
    width: 28px;
  }

}
</style>