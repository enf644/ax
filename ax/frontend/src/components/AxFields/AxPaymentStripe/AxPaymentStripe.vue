<template>
  <div>
    <div class='label'>{{name}}</div>
    <div class='hint' v-show='this.options.hint'>{{this.options.hint}} &nbsp;</div>

    <div v-if='keyAndIntentAvaluble && paymentSuccessful == false'>
      <div class='stripe-card' ref='card'></div>
      <div class='stripe-actions'>
        <v-btn :disabled='buttonIsDisabled' @click='doPayment' class='submit-btn' small>
          <i class='far fa-credit-card'></i>
          &nbsp; {{buttonText}}
          <i
            class='fas fa-spinner fa-spin action-loading'
            v-if='buttonIsDisabled'
          ></i>
        </v-btn>
        <v-btn :disabled='refreshLoading' @click='getStripeIntent' icon>
          <i :class='refreshIconClass'></i>
        </v-btn>
      </div>
    </div>

    <div class='ok-div' v-if='keyAndIntentAvaluble && paymentSuccessful'>
      <i class='far fa-check-circle big-ok'></i>
      &nbsp;&nbsp;
      <b>{{successMessage}}</b>
    </div>

    <v-alert
      :value='true'
      type='warning'
      v-if='this.stripeNotAvalible == false && this.keyAndIntentAvaluble == false'
    >{{locale('types.AxPaymentStripe.intent-not-set')}}</v-alert>

    <v-alert
      :value='true'
      type='warning'
      v-if='this.stripeNotAvalible'
    >{{locale('types.AxPaymentStripe.stripe-not-avalible')}}</v-alert>

    <hr :class='errorClass' />
    <transition enter-active-class='animated shake' leave-active-class='animated fadeOut'>
      <div class='required-error' v-show='errorString'>{{errorString}}</div>
    </transition>
  </div>
</template>

<script>
import i18n from '@/locale.js';
import apolloClient from '@/apollo';
import gql from 'graphql-tag';
import { injectScript } from '@/misc';

export default {
  name: 'AxRadio',
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
    currentValue: null,
    errors: [],
    stripe: null,
    elements: null,
    card: null,
    buttonIsDisabled: false,
    refreshLoading: false
  }),
  computed: {
    stripeNotAvalible() {
      if (typeof Stripe !== 'undefined') return false;
      return true;
    },
    keyAndIntentAvaluble() {
      if (
        this.currentValue &&
        this.currentValue.pubKey &&
        this.currentValue.intent &&
        !this.stripeNotAvalible
      )
        return true;
      return false;
    },
    amount() {
      const floatAmount = this.currentValue.intent.amount / 100;
      return floatAmount.toLocaleString();
    },
    currency() {
      const cur = this.currentValue.intent.currency;
      if (cur == 'usd') return '$';
      if (cur == 'rub') return '₽';
      if (cur == 'eur') return '€';
      return cur.toUpperCase();
    },
    buttonText() {
      if (this.options.buttonText) return this.options.buttonText;
      return this.locale('types.AxPaymentStripe.button-default', {
        amount: this.amount,
        currency: this.currency
      });
    },
    successMessage() {
      if (this.options.successMessage) return this.options.successMessage;
      return this.locale('types.AxPaymentStripe.success-message-default', {
        amount: this.amount,
        currency: this.currency
      });
    },
    paymentSuccessful() {
      if (
        this.keyAndIntentAvaluble &&
        this.currentValue.intent.status == 'succeeded'
      )
        return true;
      return false;
    },
    errorString() {
      if (this.errors.length > 0) return this.errors.join('. ');
      return false;
    },
    errorClass() {
      if (this.errors.length > 0) return 'hr-error';
      return null;
    },
    refreshIconClass() {
      if (this.refreshLoading) 'fas fa-sync-alt fa-spin';
      return 'fas fa-sync-alt';
    }
  },
  watch: {
    currentValue(newValue) {
      this.$emit('update:value', newValue);
    },
    value(newValue) {
      this.currentValue = newValue;
      setTimeout(() => {
        this.initStripe();
      }, 100);
    }
  },
  created() {
    this.currentValue = this.value;
  },
  mounted() {
    this.initStripe();
  },
  methods: {
    locale(key, param = null) {
      return i18n.t(key, param);
    },
    initStripe() {
      if (
        this.keyAndIntentAvaluble &&
        this.stripe == null &&
        this.paymentSuccessful == false
      ) {
        this.stripe = Stripe(this.currentValue.pubKey);
        this.elements = this.stripe.elements();

        this.card = this.elements.create('card');
        this.card.mount(this.$refs.card);

        this.card.addEventListener('change', ({ error }) => {
          if (error) {
            this.errors.push(error.message);
          } else {
            this.errors = [];
          }
        });
      }
    },
    doPayment() {
      let self = this;
      this.buttonIsDisabled = true;

      const clientSecret = this.currentValue.intent.client_secret;
      this.stripe
        .confirmCardPayment(clientSecret, {
          payment_method: { card: this.card }
        })
        .then(result => {
          this.buttonIsDisabled = false;
          if (result.error) {
            // Show error to your customer (e.g., insufficient funds)
            this.errors.push(result.error.message);
          } else {
            // The payment has been processed!
            if (result.paymentIntent.status === 'succeeded') {
              let newValue = Object.assign({}, this.currentValue);
              newValue.intent = result.paymentIntent;
              this.currentValue = newValue;
              // Show a success message to your customer
              // There's a risk of the customer closing the window before callback
              // execution. Set up a webhook or plugin to listen for the
              // payment_intent.succeeded event that handles any business critical
              // post-payment actions.
            }
          }
        });
    },
    isValid() {
      this.errors = [];
      if (this.requiredIsValid()) return true;
      return false;
    },
    requiredIsValid() {
      if (this.isRequired && this.keyAndIntentAvaluble) {
        if (!this.currentValue || this.paymentSuccessful == false) {
          let msg = i18n.t('types.AxPaymentStripe.required-default');
          if (this.options.required_text) msg = this.options.required_text;
          this.errors.push(msg);
          return false;
        }
        this.errors = [];
        return true;
      }
      return true;
    },
    getStripeIntent() {
      this.refreshLoading = true;

      const GET_INTENT = gql`
        mutation($intenId: String!) {
          getStripeIntent(intenId: $intenId) {
            intent
            ok
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: GET_INTENT,
          variables: {
            intenId: this.currentValue.intent.id
          }
        })
        .then(data => {
          const recivedIntent = data.data.getStripeIntent.intent;
          this.currentValue.intent = JSON.parse(recivedIntent);
          this.refreshLoading = false;
        })
        .catch(error => {
          this.$log.error(`Error in getStripeIntent apollo client => ${error}`);
        });
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
.hint {
  color: rgba(0, 0, 0, 0.54);
  font-size: 12px;
  margin-top: '5px' !important;
}
.stripe-card {
  padding: 15px 0px 15px 0px;
  border: 1px solid #ccc;
  padding-left: 10px;
  border-radius: 3px;
  margin: 5px 0px 20px 0px;
}
.hr-error {
  border-color: #b71c1c;
}
.submit-btn {
  margin-bottom: 10px;
}
.stripe-actions {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
.action-loading {
  margin-left: 15px;
  color: #f44336;
}
.big-ok {
  font-size: 20px;
  color: #4caf50;
}
.ok-div {
  margin: 15px 0px 15px 0px;
}
</style>
