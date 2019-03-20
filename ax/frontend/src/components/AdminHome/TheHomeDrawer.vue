<template>
  <div>
    <div ref='tree'></div>
    <br>
    <br>
    <v-btn @click='openModal'>
      <font-awesome-icon class='breadcrumbs-action' icon='plus'/>&nbsp; Add new form
    </v-btn>

    <!--  transition='animated flipInX faster' -->
    <modal adaptive height='auto' name='new-form'>
      <TheNewForm @created='closeModal'/>
    </modal>
    <br>
    <br>
    <br>

    <ul>
      <li :key='form.dbName' v-for='form in forms'>{{ form.dbName }}</li>
    </ul>

    <br>
    <br>
    <br>
    <li>
      <router-link to='/admin/alfa_obj/form'>Alfa</router-link>
    </li>
    <li>
      <router-link to='/admin/beta_obj/form'>Beta</router-link>
    </li>
    <li>
      <router-link to='/admin/gamma_obj/form'>Gamma</router-link>
    </li>

    <hr>
    <li>
      <router-link to='/admin/users'>Users</router-link>
    </li>
    <li>
      <router-link to='/admin/marketplace'>Marketplace</router-link>
    </li>
    <li>
      <router-link to='/admin/deck'>Deck designer</router-link>
    </li>
  </div>
</template>

<script>
import $ from 'jquery';
import 'jstree/dist/jstree.js';
import 'jstree/dist/themes/default/style.css';
import TheNewForm from '@/components/AdminHome/TheNewForm.vue';

export default {
  name: 'home-drawer',
  components: {
    TheNewForm
  },
  data() {
    return {};
  },
  computed: {
    forms() {
      return this.$store.state.form.forms;
    }
  },
  created() {
    this.$store.dispatch('form/getAllForms');
  },
  mounted() {
    // this.$log.info();
    window.jQuery = $;
    window.$ = $;
    $(this.$refs.tree).jstree({
      core: {
        data: [
          {
            text: 'Root node',
            children: [{ text: 'Child node 1' }, { text: 'Child node 2' }]
          }
        ]
      }
    });
  },
  methods: {
    openModal() {
      this.$modal.show('new-form');
    },
    closeModal() {
      this.$modal.hide('new-form');
    },
    creteNewForm() {
      this.$log.info('Create form');
    }
  }
};
</script>

<style scoped>
</style>
