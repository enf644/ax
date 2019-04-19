<template>
  <div>
    <h1>Workflow content</h1>
    <div class='footer'>
      <v-btn
        :to='"/admin/" + this.$route.params.db_name + "/grids/" + defaultGridDbName'
        class='constructor-button'
        flat
        small
      >
        &nbsp;
        <b>Next</b> &nbsp;
        <i class='fas fa-arrow-right'></i> &nbsp;
        build Grids
        &nbsp;
        <i class='fas fa-columns'></i>
      </v-btn>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WorkflowConstructorContent',
  computed: {
    defaultGridDbName() {
      const defaultGrid = this.$store.state.form.grids.find(
        grid => grid.isDefaultView === true
      );
      return defaultGrid ? defaultGrid.dbName : null;
    }
  }
};
</script>

<style scoped>
.footer {
  position: absolute;
  right: 10px;
  bottom: 10px;
}
</style>
