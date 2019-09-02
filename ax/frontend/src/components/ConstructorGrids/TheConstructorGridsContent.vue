<template>
  <div class='container'>
    <ax-grid
      :form='formDbName'
      :grid='gridDbName'
      :update_time='gridUpdateTime'
      @modify='saveGridOptions'
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

      if (data.name === 'filter-change') {
        this.$store.commit('grids/setFilterModel', data);
        this.$store.dispatch('grids/updateGrid', {}).then(() => {
          const msg = this.$t('grids.grid-updated');
          this.$dialog.message.success(
            `<i class="fas fa-columns"></i> &nbsp ${msg}`
          );
        });
      }

      if (data.name === 'sort-change') {
        this.$store.commit('grids/setSortModel', data);
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
