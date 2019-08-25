<template>
  <div class='root-div'>
    <div v-if='this.options.comparator'>
      <span class='label'>{{currentName}}</span>
      <div class='value-div'>{{value}}</div>
      <hr />
    </div>
    <v-tooltip bottom>
      <template v-slot:activator='{ on }'>
        <div class='link-btn'>
          <transition enter-active-class='animated bounce'>
            <v-btn @click='copyLink' flat icon ref='linkBtn' v-if='btnIsVisible' v-on='on'>
              <i class='fas fa-anchor'></i>
            </v-btn>
          </transition>
        </div>
      </template>
      <span>{{locale("types.AxNum.link-tooltip")}}</span>
    </v-tooltip>

    <v-alert
      :value='true'
      type='warning'
      v-if='!this.options.comparator'
    >{{locale("common.no-field-settings-error", {name: this.name})}}</v-alert>
  </div>
</template>

<script>
import copy from 'copy-to-clipboard';
import { getAxHost, getAxProtocol } from '@/misc';
import i18n from '@/locale';

export default {
  name: 'AxNum',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null,
    formDbName: null
  },
  data: () => ({
    errors: [],
    btnIsVisible: true
  }),
  computed: {
    currentName() {
      if (!this.name) return '';
      return this.name;
    }
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    },
    copyLink() {
      const url = `${getAxProtocol()}://${getAxHost()}/form/${
        this.formDbName
      }/${this.value}`;
      copy(url);
      this.btnIsVisible = false;
      setTimeout(() => {
        this.btnIsVisible = true;
      }, 1);
    }
  }
};
</script>

<style scoped>
.root-div {
  position: relative;
}
.link-btn {
  position: absolute;
  right: 0px;
  top: 0px;
}
.label {
  font-size: 13px;
  color: #000;
  opacity: 0.54;
}
.value-div {
  min-height: 26px;
  font-size: 16px;
  font-weight: bold;
}
</style>
