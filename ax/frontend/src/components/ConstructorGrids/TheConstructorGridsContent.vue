<template>
  <div class='container'>
    <ax-grid
      :constructor_mode='true'
      :form='formDbName'
      :grid='gridDbName'
      :update_time='gridUpdateTime'
      @modify='saveGridOptions'
      ref='grid'
    ></ax-grid>
  </div>
</template>

<script>
import AxGrid from '@/components/AxGrid.vue';

export default {
  name: 'ConstructorGridContent',
  components: { AxGrid },
  data: () => ({}),
  computed: {
    formDbName() {
      return this.$route.params.db_name;
    },
    gridDbName() {
      return this.$route.params.grid_alias;
    },
    gridUpdateTime() {
      return this.$store.state.grids.updateTime;
    },
    doSaveSortFilterModel() {
      return this.$store.state.grids.doSaveSortFilterModel;
    }
  },
  watch: {
    doSaveSortFilterModel(newValue) {
      if (newValue) {
        this.$store.commit(
          'grids/setFilterModel',
          this.$refs.grid.getFilterModel()
        );
        this.$store.commit(
          'grids/setSortModel',
          this.$refs.grid.getSortModel()
        );
        this.$store.commit('grids/setDoSaveSortFilterModel', false);
        this.$store.dispatch('grids/updateGrid', {}).then(() => {
          const msg = this.$t('grids.grid-updated');
          this.$dialog.message.success(
            `<i class="fas fa-columns"></i> &nbsp ${msg}`
          );
        });
      }
    }
  },
  methods: {
    saveGridOptions(data) {
      if (data.name === 'column-width') {
        this.$store.commit('grids/setColumnWidth', data);
        this.$store.dispatch('grids/updateGrid', {}).then(() => {
          const msg = this.$t('grids.grid-updated');
          this.$dialog.message.success(
            `<i class="fas fa-columns"></i> &nbsp ${msg}`
          );
        });
      }
    }
  }
};
</script>

<style scoped>
.container {
  /* padding: 20px;*/
  /* height: 100%; */
  margin-top: 40px;
  height: calc(100% - 60px);
  position: relative;
}
</style>
