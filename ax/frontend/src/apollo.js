import { ApolloClient } from 'apollo-client';
import { WebSocketLink } from 'apollo-link-ws';
import { split } from 'apollo-link';
import { HttpLink } from 'apollo-link-http';
import { getMainDefinition } from 'apollo-utilities';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { getAxHost } from './misc';
import logger from './logger';

const axHost = getAxHost();

const httpLink = new HttpLink({
  uri: `http://${axHost}/api/graphql`
});
const wsLink = new WebSocketLink({
  uri: `ws://${axHost}/api/subscriptions`,
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

logger.info(`Ax -> GraphQL is looking at ${axHost}`);

export default apolloClient;
