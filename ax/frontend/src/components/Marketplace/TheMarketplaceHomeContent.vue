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
  computed: {
    searchString() {
      return this.$store.state.home.marketSearchString;
    }
  },
  watch: {
    searchString(newValue) {
      this.gridObj.gridOptions.api.setQuickFilter(newValue);
    }
  },
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
            if (params.data.usesPro)
              return `<div class='icon-box-pro'><i class='${params.value}'></i></div>`;
            return `<div class='icon-box'><i class='${params.value}'></i></div>`;
          }
        },
        {
          headerName: 'Name',
          field: 'name',
          width: 250,
          cellStyle: {
            'white-space': 'normal',
            'line-height': 'normal',
            'padding-top': '15px'
          }
        },
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
          width: 250,
          cellRenderer: params => {
            const url = `https://github.com/${params.value}`;
            return `<a href='${url}' target='_blank'>${params.value}</a>`;
          }
        },
        {
          headerName: 'Tags',
          field: 'tags',
          width: 300
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
      axios.get(`${this.host}/api/marketplace_all`).then(response => {
        if (
          response &&
          response.data &&
          response.data.data &&
          response.data.data.AxAppsPublished
        ) {
          this.apps = response.data.data.AxAppsPublished;
          this.initAgGrid();
        } else {
          console.log(response);
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