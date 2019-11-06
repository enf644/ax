<template>
  <div class='terminal-wrapper'>
    <div class='terminal-div' ref='terminalDiv'></div>
  </div>
</template>

<script>
import uuid4 from 'uuid4';
import { Terminal } from 'xterm';
import { WebLinksAddon } from 'xterm-addon-web-links';
import { FitAddon } from 'xterm-addon-fit';
import { SearchAddon } from 'xterm-addon-search';
import 'xterm/css/xterm.css';
import apolloClient from '@/apollo';
import gql from 'graphql-tag';

export default {
  name: 'AxTerminal',
  components: {},
  props: {
    modalGuid: String
  },
  data: () => ({
    terminal: null,
    terminalGuid: null
  }),
  computed: {},
  watch: {},
  created() {
    if (this.modalGuid) this.terminalGuid = this.modalGuid;
    else this.terminalGuid = uuid4();
  },
  mounted() {
    this.initiateTerminal();
    setTimeout(() => {
      this.terminal.open(this.$refs.terminalDiv);
      // this.terminal.fit();
    }, 500);
    this.subscribeToTerminal();
  },
  methods: {
    initiateTerminal() {
      this.terminal = new Terminal({
        fontSize: 14,
        fontFamily: 'Consolas, courier-new, courier, sans-serif'
      });

      this.terminal.setOption('theme', { background: '#1e1e1e' });
      this.terminal.setOption('cursorBlink', false);
      this.terminal.setOption('convertEol', true);
      this.terminal.loadAddon(new FitAddon());
      this.terminal.loadAddon(new SearchAddon());
      this.terminal.loadAddon(new WebLinksAddon());
    },
    subscribeToTerminal() {
      const TERMINAL_SUBSCRIPTION_QUERY = gql`
        subscription($modalGuid: String!) {
          consoleNotify(modalGuid: $modalGuid) {
            modalGuid
            text
          }
        }
      `;

      apolloClient
        .subscribe({
          query: TERMINAL_SUBSCRIPTION_QUERY,
          variables: {
            modalGuid: this.terminalGuid
          }
        })
        .subscribe(
          data => {
            const msg = data.data.consoleNotify.text;
            console.log(msg);

            this.terminal.write(`${msg}`);
            return true;
          },
          {
            error(error) {
              this.$log.error(`AxTerminal -> subscribeToTerminal => ${error}`);
            }
          }
        );
      return true;
    }
  }
};
</script>

<style scoped>
.terminal-wrapper {
  margin: 10px 25px 25px 25px;
  padding: 20px;
  background: #1e1e1e;
}
</style>