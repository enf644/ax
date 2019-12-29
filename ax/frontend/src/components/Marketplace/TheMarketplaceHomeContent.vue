<template>
  <div class='app-grid-wrapper'>
    <div class='app-grid ag-theme-material' ref='grid'></div>
  </div>
</template>

<script>
// import CatalogItem from '@/components/CatalogItem.vue';
import { getAxHostProtocol, openInTab } from '@/misc';
import axios from 'axios';
import i18n from '@/locale';
import { Grid } from 'ag-grid-community';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-material.css';

export default {
  name: 'TheMarketplaceHomeContent',
  components: {},
  data: () => ({
    apps: null
  }),
  computed: {},
  watch: {},
  mounted() {
    this.host = getAxHostProtocol();
    this.getApps();
  },
  methods: {
    initAgGrid() {
      const columnDefs = [
        {
          headerName: 'Icon',
          field: 'icon',
          width: 100,
          cellRenderer: params => {
            return `<div class='icon-box'><i class='${params.value}'></i></div>`;
          }
        },
        { headerName: 'Name', field: 'name', width: 250 },
        {
          headerName: 'Description',
          field: 'shortText',
          width: 250,
          cellStyle: {
            'white-space': 'normal',
            'line-height': 'normal',
            'padding-top': '15px'
          }
        },
        {
          headerName: 'Repo',
          field: 'repo',
          width: 300,
          cellRenderer: params => {
            const url = `https://github.com/${params.value}`;
            return `<a href='${url}' target='_blank'>${params.value}</a>`;
          }
        }
      ];

      // let the grid know which columns and what data to use
      let gridOptions = {
        columnDefs: columnDefs,
        rowData: this.apps
      };

      gridOptions.onRowClicked = event => this.setActiveRepo(event);
      gridOptions.rowHeight = 80;
      this.gridObj = new Grid(this.$refs.grid, gridOptions);
    },
    getApps() {
      console.log('getApps');
      axios.get(`${this.host}/api/marketplace_all`).then(response => {
        if (
          response &&
          response.data &&
          response.data.data &&
          response.data.data.AxApps
        ) {
          this.apps = response.data.data.AxApps;
          this.initAgGrid();
        }
      });
    },
    setActiveRepo(event) {
      this.$store.commit('home/setMarketActiveRepo', event.data.repo);
    }
  }
};
</script>

<style scoped>
.app-grid-wrapper {
  width: 100%;
  height: 100%;
}
.app-grid {
  width: 100%;
  height: 100%;
}
</style>