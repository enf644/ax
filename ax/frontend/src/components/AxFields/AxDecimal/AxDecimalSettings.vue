<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    <v-container>
      <v-row>
        <v-col>
          <v-text-field
            :hint='locale("types.AxDecimal.currencySymbol-hint")'
            :label='locale("types.AxDecimal.currencySymbol-label")'
            persistent-hint
            v-model='changedOptions.currencySymbol'
          ></v-text-field>
        </v-col>
        <v-col>
          <v-text-field
            :label='locale("types.AxDecimal.decimalCharacter-label")'
            persistent-hint
            v-model='changedOptions.decimalCharacter'
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-text-field
            :label='locale("types.AxDecimal.decimalPlaces-label")'
            persistent-hint
            v-model='changedOptions.decimalPlaces'
          ></v-text-field>
        </v-col>
        <v-col>
          <v-text-field
            :label='locale("types.AxDecimal.digitGroupSeparator-label")'
            persistent-hint
            v-model='changedOptions.digitGroupSeparator'
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-text-field
            :hint='locale("types.AxDecimal.wheelStep-hint")'
            :label='locale("types.AxDecimal.wheelStep-label")'
            persistent-hint
            v-model='changedOptions.wheelStep'
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-text-field
            :label='locale("types.AxDecimal.minimumValue-label")'
            persistent-hint
            v-model='changedOptions.minimumValue'
          ></v-text-field>
        </v-col>
        <v-col>
          <v-text-field
            :label='locale("types.AxDecimal.maximumValue-label")'
            persistent-hint
            v-model='changedOptions.maximumValue'
          ></v-text-field>
        </v-col>
      </v-row>
    </v-container>
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '@/locale.js';

export default {
  name: 'AxDecimalSettings',
  components: { AxFieldSettings },
  props: {
    guid: null,
    options: null
  },
  data: () => ({
    changedOptions: {},
    errors: []
  }),
  created() {
    this.changedOptions = this.options;
    if (!this.changedOptions.decimalCharacter)
      this.changedOptions.decimalCharacter = ',';
    if (!this.changedOptions.decimalPlaces)
      this.changedOptions.decimalPlaces = 2;
    if (!this.changedOptions.digitGroupSeparator)
      this.changedOptions.digitGroupSeparator = ' ';
    if (!this.changedOptions.wheelStep) this.changedOptions.wheelStep = 1;
    if (!this.changedOptions.minimumValue) this.changedOptions.minimumValue = 0;
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    }
  }
};
</script>

<style scoped>
</style>
