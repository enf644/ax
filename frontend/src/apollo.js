import { ApolloClient } from 'apollo-client';
import { WebSocketLink } from 'apollo-link-ws';
import { split } from 'apollo-link';
import { HttpLink } from 'apollo-link-http';
import { getMainDefinition } from 'apollo-utilities';
import { InMemoryCache } from 'apollo-cache-inmemory';

const httpLink = new HttpLink({
  uri: 'http://127.0.0.1:8080/api/graphql'
  // TODO get IP from settings
});
const wsLink = new WebSocketLink({
  uri: 'ws://127.0.0.1:8080/api/subscriptions',
  options: {
    reconnect: true
  }
});
const link = split(
  ({ query }) => {
    const { kind, operation } = getMainDefinition(query);
    return kind === 'OperationDefinition' && operation === 'subscription';
  },
  wsLink,
  httpLink
);
const cache = new InMemoryCache();
const apolloClient = new ApolloClient({ link, cache });

export default apolloClient;
