<template>
  <div class='test-container align-stretch' elevation='5' light ref='sheet' v-if='routeForm'>
    <AxGrid :form='routeForm' :grid='routeGrid'></AxGrid>
  </div>
</template>

<script>
import AxGrid from '@/components/AxGrid.vue';

export default {
  name: 'TheExplorerContent',
  components: { AxGrid },
  data: () => ({
    // currentForm: null,
    // currentGrid: null
  }),
  computed: {
    routeForm() {
      return this.$route.params.form;
    },
    routeGrid() {
      return this.$route.params.grid;
    }
  },
  watch: {
    // routeForm(newValue) {
    //   if (newValue) {
    //     this.currentForm = newValue;
    //     this.currentGrid = newValue;
    //   }
    // }
  },
  mounted() {
    // console.log();
  },
  methods: {}
};
</script>

<style scoped>
.test-container {
  /* width: calc(100% - 40px); */
  height: 100%;
  /* padding: 20px; */
}
</style>
