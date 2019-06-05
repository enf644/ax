<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    <br>
    <v-autocomplete
      :items='axForms'
      :label='locale("types.Ax1to1.settings-form-select")'
      :rules='formRules'
      @change='setDefaultGrid()'
      chips
      dense
      hide-selected
      item-text='name'
      item-value='dbName'
      v-model='changedOptions.form'
    >
      <template v-slot:selection='{ item, selected }'>
        <v-chip @input='clearForm()' close>
          <v-avatar class='grey'>
            <i :class='`ax-chip-icon fas fa-${item.icon}`'></i>
          </v-avatar>
          {{item.name}}
        </v-chip>
      </template>
    </v-autocomplete>
    <br>
    <v-autocomplete
      :hint='locale("types.Ax1tomTable.settings-inline-grid-hint")'
      :items='axGrids'
      :label='locale("types.Ax1tomTable.settings-inline-grid-select")'
      :rules='gridRules'
      chips
      hide-selected
      item-text='name'
      item-value='dbName'
      persistent-hint
      v-model='changedOptions.inline_grid'
    >
      <template v-slot:selection='{ item, selected }'>
        <v-chip @input='clearInlineGrid()' close>
          <v-avatar class='grey'>
            <i :class='`ax-chip-icon fas fa-columns`'></i>
          </v-avatar>
          {{item.name}}
        </v-chip>
      </template>
    </v-autocomplete>
    <br>
    <v-autocomplete
      :hint='locale("types.Ax1to1.settings-grid-hint")'
      :items='axGrids'
      :label='locale("types.Ax1to1.settings-grid-select")'
      :rules='gridRules'
      chips
      hide-selected
      item-text='name'
      item-value='dbName'
      persistent-hint
      v-model='changedOptions.grid'
    >
      <template v-slot:selection='{ item, selected }'>
        <v-chip @input='clearGrid()' close>
          <v-avatar class='grey'>
            <i :class='`ax-chip-icon fas fa-columns`'></i>
          </v-avatar>
          {{item.name}}
        </v-chip>
      </template>
    </v-autocomplete>
    <br>
    {{locale("types.Ax1tomTable.settings-inline-height")}}
    <v-slider max='1000' min='300' thumb-label v-model='changedOptions.inline_height'></v-slider>
    {{locale("types.Ax1to1.settings-height")}}
    <v-slider max='2000' min='300' thumb-label v-model='changedOptions.height'></v-slider>
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '../../../locale.js';

export default {
  name: 'Ax1tomSettings',
  components: { AxFieldSettings },
  props: {
    guid: null,
    options: null
  },
  data: () => ({
    changedOptions: {},
    errors: [],
    formRules: [v => !!v || i18n.t('common.field-required')],
    gridRules: [v => !!v || i18n.t('common.field-required')]
  }),
  computed: {
    axForms() {
      return this.$store.state.home.forms;
    },
    axGrids() {
      const selectedForm = this.$store.state.home.forms.find(
        form => form.dbName === this.changedOptions.form
      );
      return selectedForm
        ? selectedForm.grids.edges.map(edge => edge.node)
        : [];
    }
  },
  created() {
    this.changedOptions = this.options;
    if (!this.changedOptions.isWholeRow) this.changedOptions.isWholeRow = true;
    if (!this.changedOptions.height) this.changedOptions.height = 400;
    if (!this.changedOptions.inline_height) {
      this.changedOptions.inline_height = 400;
    }
    if (!this.changedOptions.enableFormModal) {
      this.changedOptions.enableFormModal = true;
    }
  },
  mounted() {},
  methods: {
    locale(key) {
      return i18n.t(key);
    },
    clearForm() {
      this.changedOptions.form = null;
      this.changedOptions.grid = null;
    },
    clearInlineGrid() {
      this.changedOptions.inline_grid = null;
    },
    clearGrid() {
      this.changedOptions.grid = null;
    },
    setDefaultGrid() {
      const selectedForm = this.$store.state.home.forms.find(
        form => form.dbName === this.changedOptions.form
      );
      if (selectedForm) {
        const defaultGrid = selectedForm.grids.edges.find(
          edge => edge.node.isDefaultView
        );
        if (defaultGrid) {
          this.changedOptions.grid = defaultGrid.node.dbName;
          this.changedOptions.inline_grid = defaultGrid.node.dbName;
        }
      }
    }
  }
};
</script>

<style scoped>
.editor {
  width: 100%;
  height: 400px;
}
</style>
