<template>
  <div>
    <v-btn @click='startTour()' icon>
      <i class='tour-ico far fa-life-ring'></i>
    </v-btn>
  </div>
</template>

<script>
// import CatalogItem from '@/components/CatalogItem.vue';
import i18n from '@/locale';
import 'intro.js/minified/introjs.min.css';
// import 'intro.js/themes/introjs-nassim.css';
// import 'intro.js/themes/introjs-nazanin.css';
// import 'intro.js/themes/introjs-modern.css';
// 'a[data-a="1"]'

export default {
  name: 'AxTour',
  components: {},
  data: () => ({
    introJS: null
  }),
  computed: {},
  watch: {},
  mounted() {
    const intr = require('intro.js');
    this.introJS = intr.introJs();
  },
  methods: {
    locale(key, params) {
      return i18n.t(key, params);
    },
    startTour() {
      const steps = this.getSteps(this.$route.name);

      this.introJS.setOptions({
        steps: steps,
        overlayOpacity: 0.3,
        nextLabel: this.$t('tour.nextLabel'),
        prevLabel: this.$t('tour.prevLabel'),
        skipLabel: this.$t('tour.skipLabel'),
        doneLabel: this.$t('tour.doneLabel'),
        tooltipClass: 'wide-ax-hint'
      });
      this.introJS.start();
    },
    getSteps(route) {
      // {
      //   element: document.querySelector("[data-cy='']"),
      //   intro: ""
      // },

      // HOME
      if (this.$route.name == 'admin-home')
        return [
          {
            intro: this.locale('tour.admin-home.step1')
          },
          {
            element: document.querySelector("[data-cy='create-form-btn']"),
            intro: this.locale('tour.admin-home.step2')
          },
          {
            element: document.querySelector("[data-cy='create-folder-btn']"),
            intro: this.locale('tour.admin-home.step3')
          },
          {
            element: document.querySelector("[data-cy='manage-users-btn']"),
            intro: this.locale('tour.admin-home.step4')
          },
          {
            element: document.querySelector("[data-cy='marketplace-btn']"),
            intro: this.locale('tour.admin-home.step5')
          },
          {
            element: document.querySelector("[data-cy='pages-designer-btn']"),
            intro: this.locale('tour.admin-home.step6')
          },
          {
            element: document.querySelector("[data-cy='data-explorer-btn']"),
            intro: this.locale('tour.admin-home.step7')
          }
        ];

      // FORM
      if (this.$route.name == 'admin-form')
        return [
          {
            intro: this.locale('tour.admin-form.step1')
          },
          {
            element: document.querySelector("[data-cy='types-tree']"),
            intro: this.locale('tour.admin-form.step2')
          },
          {
            element: document.querySelector("[data-cy='fields-tree']"),
            intro: this.locale('tour.admin-form.step3')
          },
          {
            intro: this.locale('tour.admin-form.step4')
          },
          {
            element: document.querySelector("[data-cy='add-tab-btn']"),
            intro: this.locale('tour.admin-form.step5')
          },
          {
            element: document.querySelector("[data-cy='update-form-btn']"),
            intro: this.locale('tour.admin-form.step6')
          },
          {
            element: document.querySelector("[data-cy='copy-url-btn']"),
            intro: this.locale('tour.admin-form.step7')
          },
          {
            element: document.querySelector("[data-cy='ax-form-header']"),
            intro: this.locale('tour.admin-form.step8')
          },
          {
            element: document.querySelector("[data-cy='copy-tag-btn']"),
            intro: this.locale('tour.admin-form.step9')
          }
        ];

      // GRIDS
      if (this.$route.name == 'admin-grids')
        return [
          {
            intro: this.locale('tour.admin-grids.step1')
          },
          {
            element: document.querySelector("[data-cy='grid-fields-tree']"),
            intro: this.locale('tour.admin-grids.step2')
          },
          {
            element: document.querySelector("[data-cy='columns-tree']"),
            intro: this.locale('tour.admin-grids.step3')
          },
          {
            element: document.querySelector("[data-cy='grid-options-btn']"),
            intro: this.locale('tour.admin-grids.step4')
          },
          {
            element: document.querySelector("[data-cy='grid-select-btn']"),
            intro: this.locale('tour.admin-grids.step5')
          },
          {
            element: document.querySelector("[data-cy='save-grid-model-btn']"),
            intro: this.locale('tour.admin-grids.step6')
          },
          {
            element: document.querySelector("[data-cy='query-modal-btn']"),
            intro: this.locale('tour.admin-grids.step7')
          },
          {
            element: document.querySelector("[data-cy='options-quick-search']"),
            intro: this.locale('tour.admin-grids.step8')
          },
          {
            element: document.querySelector("[data-cy='options-enable-title']"),
            intro: this.locale('tour.admin-grids.step9')
          },
          {
            element: document.querySelector("[data-cy='options-flat-mode']"),
            intro: this.locale('tour.admin-grids.step10')
          },
          {
            element: document.querySelector("[data-cy='options-subscription']"),
            intro: this.locale('tour.admin-grids.step11')
          },
          {
            element: document.querySelector(
              "[data-cy='options-columns-resize']"
            ),
            intro: this.locale('tour.admin-grids.step12')
          },
          {
            element: document.querySelector("[data-cy='options-filtering']"),
            intro: this.locale('tour.admin-grids.step13')
          },
          {
            element: document.querySelector("[data-cy='options-soring']"),
            intro: this.locale('tour.admin-grids.step14')
          },
          {
            element: document.querySelector("[data-cy='options-open-form']"),
            intro: this.locale('tour.admin-grids.step15')
          },
          {
            element: document.querySelector("[data-cy='options-actions']"),
            intro: this.locale('tour.admin-grids.step16')
          },
          {
            element: document.querySelector("[data-cy='options-row-height']"),
            intro: this.locale('tour.admin-grids.step17')
          },
          {
            element: document.querySelector("[data-cy='options-pinned']"),
            intro: this.locale('tour.admin-grids.step18')
          },
          {
            element: document.querySelector("[data-cy='copy-url-btn']"),
            intro: this.locale('tour.admin-grids.step19')
          },
          {
            element: document.querySelector("[data-cy='copy-tag-btn']"),
            intro: this.locale('tour.admin-grids.step20')
          },
          {
            element: document.querySelector("[data-cy='copy-graphql-btn']"),
            intro: this.locale('tour.admin-grids.step21')
          }
        ];

      // WORKFLOW
      if (this.$route.name == 'admin-workflow')
        return [
          {
            intro: this.locale('tour.admin-workflow.step1')
          },
          {
            intro: this.locale('tour.admin-workflow.step2')
          },
          {
            intro: this.locale('tour.admin-workflow.step3')
          },
          {
            intro: this.locale('tour.admin-workflow.step4')
          },
          {
            intro: this.locale('tour.admin-workflow.step5')
          },
          {
            intro: this.locale('tour.admin-workflow.step6')
          },
          {
            element: document.querySelector("[data-cy='create-role-btn']"),
            intro: this.locale('tour.admin-workflow.step7')
          },
          {
            intro: this.locale('tour.admin-workflow.step8')
          },
          {
            intro: this.locale('tour.admin-workflow.step9')
          },
          {
            intro: this.locale('tour.admin-workflow.step10')
          },
          {
            element: document.querySelector(
              "[data-cy='create-dynamic-role-btn']"
            ),
            intro: this.locale('tour.admin-workflow.step11')
          }
        ];

      // PAGES
      if (this.$route.name == 'admin-pages')
        return [
          {
            intro: this.locale('tour.admin-pages.step1')
          },
          {
            element: document.querySelector("[data-cy='pages-tree']"),
            intro: this.locale('tour.admin-pages.step2')
          },
          {
            element: document.querySelector("[data-cy='create-page-btn']"),
            intro: this.locale('tour.admin-pages.step3')
          },
          {
            element: document.querySelector("[data-cy='page-options-btn']"),
            intro: this.locale('tour.admin-pages.step4')
          },
          {
            intro: this.locale('tour.admin-pages.step5')
          },
          {
            intro: this.locale('tour.admin-pages.step6')
          }
        ];

      // USERS
      if (this.$route.name == 'users-manager')
        return [
          {
            intro: this.locale('tour.users-manager.step1')
          },
          {
            element: document.querySelector("[data-cy='all-users-btn']"),
            intro: this.locale('tour.users-manager.step2')
          },
          {
            element: document.querySelector("[data-cy='blocked-users-btn']"),
            intro: this.locale('tour.users-manager.step3')
          },
          {
            element: document.querySelector("[data-cy='create-user-btn']"),
            intro: this.locale('tour.users-manager.step4')
          },
          {
            element: document.querySelector("[data-cy='create-group-btn']"),
            intro: this.locale('tour.users-manager.step5')
          },
          {
            element: document.querySelector("[data-cy='groups-tree']"),
            intro: this.locale('tour.users-manager.step6')
          }
        ];

      // MARKETPLACE
      if (this.$route.name == 'admin-marketplace')
        return [
          {
            intro: this.locale('tour.admin-marketplace.step1')
          },
          {
            element: document.querySelector("[data-cy='market-search-input']"),
            intro: this.locale('tour.admin-marketplace.step2')
          },
          {
            intro: this.locale('tour.admin-marketplace.step3')
          },
          {
            intro: this.locale('tour.admin-marketplace.step4')
          },
          {
            element: document.querySelector("[data-cy='market-install-btn']"),
            intro: this.locale('tour.admin-marketplace.step5')
          },
          {
            element: document.querySelector("[data-cy='market-upload-btn']"),
            intro: this.locale('tour.admin-marketplace.step6')
          },
          {
            intro: this.locale('tour.admin-marketplace.step6')
          }
        ];
    }
  }
};
</script>

<style scoped>
.tour-ico {
  font-size: 22px;
  color: #b71c1c;
}
</style>