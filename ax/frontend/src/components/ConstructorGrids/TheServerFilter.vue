<template>
  <div class='card'>
    <h1>{{$t("grids.server-filter-header")}}</h1>
    <v-btn :ripple='false' @click='closeModal' class='close' color='black' text icon>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <div id='builder' ref='builder'></div>

    <br>
    <div class='actions'>
      <v-btn @click='saveServerFilters' small>
        <i class='fas fa-filter'></i>
        &nbsp; {{$t("common.save")}}
      </v-btn>
      <v-btn @click='closeModal' small>
        <i class='fas fa-times'></i>
        &nbsp; {{$t("common.confirm-no")}}
      </v-btn>
    </div>
  </div>
</template>

<script>
// import MonacoEditor from 'vue-monaco';

import $ from 'jquery';
import 'sql-parser-mistic/browser/sql-parser.js';
import 'jQuery-QueryBuilder/dist/js/query-builder.standalone.js';
import 'jQuery-QueryBuilder/dist/css/query-builder.default.css';

export default {
  name: 'TheServerFilter',
  data: () => ({
    builderInitialized: false,
    filterCode: null
  }),
  // components: { MonacoEditor },
  computed: {
    columns() {
      return this.$store.state.grids.columns;
    },
    filters() {
      return this.$store.getters['grids/serverFilterData'];
    },
    options() {
      return this.$store.state.grids.options;
    }
  },
  mounted() {
    if (!this.builderInitialized) this.initQueryBuilder();
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },
    saveServerFilters() {
      let currentFilter = $(this.$refs.builder).queryBuilder('getSQL', 'named');
      let currentRules = $(this.$refs.builder).queryBuilder('getRules');

      if (!currentFilter || currentFilter.sql === '') {
        currentFilter = null;
        currentRules = null;
      }

      this.$store.commit('grids/combineOptions', {
        serverFilter: currentFilter,
        serverFilterRules: currentRules
      });

      this.$store.dispatch('grids/updateGrid', {}).then(() => {
        const msg = this.$t('grids.grid-updated');
        this.$store.commit('grids/setUpdateTime', Date.now());
        this.$dialog.message.success(
          `<i class="fas fa-columns"></i> &nbsp ${msg}`
        );
        this.closeModal();
      });
    },
    initQueryBuilder() {
      const builderOptions = {
        icons: {
          add_group: 'fas fa-plus-square',
          add_rule: 'fas fa-plus-circle',
          remove_group: 'fas fa-minus-square',
          remove_rule: 'fas fa-minus-circle',
          error: 'fas fa-exclamation-triangle'
        },
        filters: this.filters
      };

      $(this.$refs.builder).queryBuilder(builderOptions);

      if (
        this.options.serverFilter != null
        && this.options.serverFilter.params != null
      ) {
        $(this.$refs.builder).queryBuilder(
          'setRules',
          this.options.serverFilterRules
        );
      } else {
        $(this.$refs.builder).queryBuilder('reset');
      }

      this.builderInitialized = true;
    }
  }
};
</script>

<style scoped>
.card {
  padding: 25px;
}
.close {
  position: absolute;
  right: 10px;
  top: 10px;
}
.close-ico {
  font-size: 20px;
}
.actions {
  justify-content: space-between;
  display: flex;
}
.editor {
  width: 100%;
  height: 400px;
}
</style>
