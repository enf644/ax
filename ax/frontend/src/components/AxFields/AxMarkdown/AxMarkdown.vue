<template>
  <div>
    <!-- <v-textarea
    :disabled='isReadonly'
    :error-messages='errors'
    :hint='options.hint'
    :label='name'
    @keyup='isValid'
    auto-grow
    v-model='currentValue'
    ></v-textarea>-->
    <span class='label'>{{name}}</span>
    <div class='markdown-body' v-html='mdValue' v-if='isReadonly'></div>
    <mavon-editor
      :externalLink='false'
      :tabSize='4'
      :toolbars='markdownOption'
      fontSize='16px'
      language='en'
      v-if='!isReadonly'
      v-model='currentValue'
    />
    <br />
    <hr :class='errorClass' />
    <transition enter-active-class='animated shake' leave-active-class='animated fadeOut'>
      <span class='required-error' v-show='errorString'>{{errorString}}</span>
    </transition>
    <span class='hint' v-show='this.options.hint'>{{this.options.hint}} &nbsp;</span>
  </div>
</template>

<script>
import Vue from 'vue';
import mavonEditor from 'mavon-editor';
import 'mavon-editor/dist/css/index.css';
// import markdownIt from 'markdown-it';

// use
Vue.use(mavonEditor);

export default {
  name: 'AxText',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null,
    isReadonly: null
  },
  data: () => ({
    currentValue: '',
    errors: [],
    mdRenderer: null,
    markdownOption: {
      bold: true,
      italic: true,
      header: true,
      underline: true,
      strikethrough: true,
      mark: false,
      superscript: false,
      subscript: false,
      quote: true,
      ol: true,
      ul: true,
      link: true,
      imagelink: true,
      code: true,
      table: true,
      fullscreen: true,
      readmodel: false,
      htmlcode: false,
      help: false,
      /* 1.3.5 */
      undo: false,
      redo: false,
      trash: false,
      save: false,
      /* 1.4.2 */
      navigation: false,
      /* 2.1.8 */
      alignleft: true,
      aligncenter: true,
      alignright: true,
      /* 2.2.1 */
      subfield: false,
      preview: false
    }
  }),
  computed: {
    mdValue() {
      return this.mdRenderer.render(this.currentValue);
    },
    errorString() {
      if (this.errors.length > 0) return this.errors.join('. ');
      return false;
    },
    errorClass() {
      if (this.errors.length > 0) return 'hr-error';
      return null;
    }
  },
  watch: {
    currentValue(newValue) {
      if (newValue != this.value) this.$emit('update:value', newValue);
    },
    value(newValue) {
      this.currentValue = newValue;
    }
  },
  created() {
    const MarkdownIt = require('markdown-it');
    this.mdRenderer = new MarkdownIt();
    this.currentValue = this.value;
    if (!this.currentValue) this.currentValue = '';
  },
  methods: {
    isValid() {
      if (this.requiredIsValid()) return true;
      return false;
    },
    requiredIsValid() {
      if (this.isRequired) {
        if (!this.currentValue || this.currentValue.length === 0) {
          this.errors.push(this.options.required_text);
          return false;
        }
        this.errors = [];
        return true;
      }
      return true;
    }
  }
};
</script>

<style scoped>
.label {
  font-size: 13px;
  color: #000;
  opacity: 0.54;
}
.required-error {
  margin-top: '5px' !important;
  color: #b71c1c;
  font-size: 12px;
  margin-right: 15px;
}
.hr-error {
  border-color: #b71c1c;
}
.hint {
  color: rgba(0, 0, 0, 0.54);
  font-size: 12px;
  margin-top: '5px' !important;
}
</style>
