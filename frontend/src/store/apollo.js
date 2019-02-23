import ApolloClient from 'apollo-boost';

const apolloClient = new ApolloClient({
  uri: 'http://127.0.0.1:8080/api/graphql'
});

// const wsClient = new SubscriptionClient('wss://127.0.0.1:8080/api/subscriptions', {
//   reconnect: true
// });

export default apolloClient;
