<template>
  <div class='chip-wrapper'>
    <v-avatar :size='size' class='chip-avatar' color='blue'>
      <span class='white--text'>
        <span v-html='showIcon'></span>
        {{twoLetters}}
      </span>
    </v-avatar>
    <div :class='shortNameClass'>{{shortName}}</div>
  </div>
</template>

<script>
// import CatalogItem from '@/components/CatalogItem.vue';

export default {
  name: 'AxUserChip',
  components: {},
  props: {
    email: null,
    size: {
      type: Number,
      default: 26
    },
    shortName: null,
    guid: null,
    currentUserEmail: null
  },
  data: () => ({}),
  computed: {
    twoLetters() {
      if (this.shortName) {
        let retStr = '';
        const capitals = this.shortName.split(' ');
        if (capitals.length > 1)
          retStr = capitals[0].substring(0, 1) + capitals[1].substring(0, 1);
        else retStr = capitals[0].substring(0, 2);
        return retStr;
      }
      return null;
    },
    showIcon() {
      if (!this.shortName) {
        return '<i class="fas fa-user-circle"></i>';
      }
      return null;
    },
    shortNameClass() {
      if (this.currentUserEmail == this.email) return 'this-is-me';
      return null;
    }
  },
  watch: {},
  mounted() {},
  methods: {}
};
</script>

<style scoped>
.chip-avatar {
  font-size: 13px;
  margin-right: 5px;
}
.this-is-me {
  font-weight: bolder;
}
.chip-wrapper {
  display: flex;
  flex-direction: row;
}
</style>