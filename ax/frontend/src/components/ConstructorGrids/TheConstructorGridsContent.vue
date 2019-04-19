<template>
  <div>
    <div>Grids content</div>
    <h1>{{ this.$store.state.grids.guid }}</h1>

    <hr>

    <AxGrid form='cars'></AxGrid>

    <!-- <ax-grid></ax-grid> -->
  </div>
</template>

<script>
import AxGrid from '@/components/AxGrid.vue';

export default {
  name: 'ConstructorGridContent',
  components: { AxGrid },
  data: () => ({})
};
</script>

<style scoped>
</style>
