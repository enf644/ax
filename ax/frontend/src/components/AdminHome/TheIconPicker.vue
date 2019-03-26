<template>
  <div class='new-form-card'>
    <h1>{{$t("home.new-form.icon-modal-header")}}</h1>
    <v-btn @click='closeModal' class='close' color='black' flat icon>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <v-text-field label='Search icons' v-model='query'/>

    <div class='flex-row'>
      <div :key='item' class='flex-cell' v-for='item in filteredItems'>
        <div @click='select(item)' class='iconbox'>
          <i :class='getIconClass(item)'></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import icons from '@/components/AdminHome/font-awesome-icons.js';

export default {
  name: 'icon-picker',
  components: {},
  props: {
    icon: String
  },
  data() {
    return {
      selected: null,
      query: null
    };
  },
  computed: {
    filteredItems() {
      // const query = this.query;
      return icons.filter(
        item => item.toLowerCase().indexOf(this.query.toLowerCase()) !== -1
      );
    }
  },
  created() {
    // TODO: Change pick component to https://codepen.io/supraniti/pen/dOxPaY
    this.query = '';
    this.selected = '';
  },
  methods: {
    select(icon) {
      this.$emit('choosed', icon);
    },
    closeModal() {
      this.$emit('choosed', null);
    },
    getIconClass(icon) {
      return `fas fa-${icon} picker`;
    }
  }
};
</script>

<style scoped>
.new-form-card {
  padding: 25px;
  text-align: center;
}
.close {
  position: absolute;
  right: 10px;
  top: 10px;
}
.close-ico {
  font-size: 20px;
}
.icon-preview {
  width: 60px !important;
  height: 60px !important;
}
.picker {
  font-size: 25px;
}
.line {
  width: 100%;
  margin: 20px;
}
.flex-cell {
  display: flex;
  flex-flow: column;
  justify-content: center;
  flex: 0 1 60px;
  height: 60px;
  text-align: center;
  transition: 0.5s;
}
.flex-cell:hover {
  background-color: gray;
  cursor: pointer;
  border-radius: 5px;
  transition: 0.2s;
}
.flex-cell:hover .caption {
  color: white;
}
.flex-row {
  display: flex;
  flex-flow: row wrap;
  justify-content: center;
}
.caption {
  padding: 2px;
  color: #757575;
  font-size: 11px;
  overflow: hidden;
  text-align: center;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.iconbox {
  word-wrap: break-word;
}
</style>
