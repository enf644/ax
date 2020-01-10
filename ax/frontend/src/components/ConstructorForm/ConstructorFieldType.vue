<template>
  <span class='wrap'>
    <v-tooltip open-delay='400' right>
      <template v-slot:activator='{ on }'>
        <span v-on='on'>
          <i :class='icon'></i>
          {{name}}
        </span>
      </template>
      <span>{{locale("types.hint-not-avalible")}}</span>
    </v-tooltip>
  </span>
</template>

<script>
//       tabindex='-1'
import i18n from '@/locale';
import store from '@/store';

export default {
  name: 'ConstructorFieldType',
  props: {
    name: null,
    icon: null,
    tag: null
  },
  data: () => ({}),
  created() {},
  mounted() {},
  methods: {
    locale(key, params) {
      return i18n.t(key, params);
    }
  }
};
</script>

<style scoped>
.wrap {
  white-space: nowrap;
}
.field-type-hint {
  margin-left: 4px;
  color: #ccc;
}
</style>
