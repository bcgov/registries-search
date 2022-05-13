<template>
  <div id="breadcrumb">
    <v-container>
      <v-row no-gutters>
        <v-col cols="auto">
          <v-btn
            id="breadcrumb-back-btn"
            class="back-btn"
            exact
            :href="backUrl"
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
                <span class="breadcrumb-text" :class="isActiveCrumb(crumb) ? 'active-crumb': 'inactive-crumb'">
                   {{ crumb.text }}
                </span>
              </div>
            </li>
          </ul>
        </div>
      </v-row>
    </v-container>
  </div>
</template>

<script lang="ts">
// External
import { defineComponent, reactive, PropType } from 'vue'
import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
import { useRoute } from 'vue-router'



export default defineComponent({
  name: 'BcrsBreadcrumb',
   props: {
    breadcrumbs: {
      type: Array as PropType<BreadcrumbIF[]>
    }
  },
  methods: {
    backUrl  () {
      console.log(this.$route)
      console.log(this.breadcrumbs)
      const routeIndex = this.breadcrumbs.findIndex(item => item.to?.name === this.$route?.name)
      const backRoute = this.breadcrumbs[routeIndex - 1]?.href || this.breadcrumbs[routeIndex - 1]?.to?.name
      return backRoute || ''
    },
    isActiveCrumb (item: BreadcrumbIF) {
      return this.$route?.name !== item?.to?.name
    }
  },
  setup(props) {
    const state = reactive({
      
    })
    const isJestRunning = (): boolean => {
      return (process.env.JEST_WORKER_ID !== undefined)
    }
    return {
     ...state,
     isJestRunning
    }
  }
})
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