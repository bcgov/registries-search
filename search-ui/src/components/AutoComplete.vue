<template>
  <v-card v-if="showAutoComplete" class="auto-complete-card" elevation="5">
    <v-row no-gutters justify="center">
      <v-col no-gutters cols="11">
        <v-item-group v-model="autoCompleteSelected">
          <v-row
            v-for="(result, i) in autoCompleteResults"
            :key="i" class="pt-0 pb-0 pl-3">
            <v-col class="title-size">
              <v-item>
                <v-label @click="autoCompleteSelected = i">{{result.value}}</v-label>
              </v-item>
            </v-col>
          </v-row>
        </v-item-group>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue';
import { getAutoComplete } from '@/utils';
import { AutoCompleteResponseIF } from '@/interfaces'; // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'AutoComplete',
  props: {
    setAutoCompleteIsActive: {
      type: Boolean,
    },
    searchValue: {
      type: String,
      default: '',
    },
  },
  setup(props, { emit }) {
    const localState = reactive({
      autoCompleteIsActive: props.setAutoCompleteIsActive,
      autoCompleteResults: [],
      autoCompleteSelected: -1,
      showAutoComplete: computed((): boolean => {
        const value =
          localState.autoCompleteResults?.length > 0 &&
          localState.autoCompleteIsActive;
        emit('hide-details', value);
        return value;
      }),
    });
    const updateAutoCompleteResults = async (searchValue: string) => {
      const response: AutoCompleteResponseIF = await getAutoComplete(
        searchValue
      );
      // check if results are still relevant before updating list
      if (searchValue === props.searchValue && response?.results) {
        // will take up to 5 results
        localState.autoCompleteResults = response?.results.slice(0, 5);
      }
    };
    watch(
      () => localState.autoCompleteSelected,
      (val: number) => {
        if (val >= 0) {
          const searchValue = localState.autoCompleteResults[val]?.value;
          localState.autoCompleteIsActive = false;
          emit('search-value', searchValue);
        }
      }
    );
    watch(
      () => localState.autoCompleteIsActive,
      (val: boolean) => {
        if (!val) localState.autoCompleteResults = [];
      }
    );
    watch(
      () => props.setAutoCompleteIsActive,
      (val: boolean) => {
        localState.autoCompleteIsActive = val;
      }
    );
    watch(
      () => props.searchValue,
      (val: string) => {
        if (localState.autoCompleteIsActive) {
          updateAutoCompleteResults(val);
        }
      }
    );

    return {
      ...toRefs(localState),
    };
  },
});
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

#auto-complete-close-btn {
  color: $gray5 !important;
  background-color: transparent !important;
}
.auto-complete-item {
  min-height: 0;
}

.auto-complete-card {
  z-index: 3;
}
.close-btn-row {
  height: 1rem;
}

.auto-complete-item:hover {
  color: $primary-blue !important;
  background-color: $gray1 !important;
}

.auto-complete-item[aria-selected='true'] {
  color: $primary-blue !important;
  background-color: $blueSelected !important;
}

.auto-complete-item:focus {
  background-color: $gray3 !important;
}

.auto-complete-row {
  width: 35rem;
  color: $gray7 !important;
}
.auto-complete-row:hover {
  color: $primary-blue !important;
}

.title-size {
  font-size: 1rem;
}
</style>
