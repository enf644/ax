<template>
  <v-app class='ax-grid-app' id='ax-grid'>
    <div class='ag-theme-material grid' ref='grid'></div>
    <!-- <modal adaptive height='auto' name='sub-form' scrollable width='70%'>
      <v-card>
        <AxForm no_margin></AxForm>
      </v-card>
    </modal>-->
  </v-app>
</template>

<script>
import { Grid } from 'ag-grid-community';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-material.css';
import AxForm from './AxForm.vue';

export default {
  name: 'AxGrid',
  components: {
    AxForm
  },
  props: {
    name: null,
    gridOptions: null
  },
  data() {
    return {
      grid: null,
      dialogIsOpen: false
    };
  },
  mounted() {
    // const debugMsg = 'Debug this Vue';

    // specify the columns
    const columnDefs = [
      { headerName: 'Make', field: 'make' },
      { headerName: 'Model', field: 'model' },
      { headerName: 'Price', field: 'price' }
    ];

    // specify the data
    const rowData = [
      { make: 'Toyota', model: 'Celica', price: 35000 },
      { make: 'Ford', model: 'Mondeo', price: 32000 },
      { make: 'Porsche', model: 'Boxter', price: 72000 }
    ];

    const gridOptions = {
      columnDefs,
      rowData
    };
    gridOptions.onRowDoubleClicked = event => this.openForm(event);
    // console.log(Grid);
    this.grid = new Grid(this.$refs.grid, gridOptions);
  },
  methods: {
    openForm(event) {
      this.$modal.show('sub-form');
      this.$log.info(event);
      // this.dialogIsOpen = true;
      // this.$modal.open(AxGridModal);
    }
  }
};
</script>

<style scoped>
.grid {
  width: 100%;
  height: 100%;
}
</style>
