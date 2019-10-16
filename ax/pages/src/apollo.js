import { ApolloClient } from 'apollo-client';
import { WebSocketLink } from 'apollo-link-ws';
import { split } from 'apollo-link';
import { HttpLink } from 'apollo-link-http';
import { getMainDefinition } from 'apollo-utilities';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { setContext } from 'apollo-link-context';
import { getAxHost, getAxWsProtocol, getAxProtocol } from './misc';
import store from './store';
// import { ApolloClient, ApolloLink, InMemoryCache, HttpLink } from 'apollo-boost';
// import logger from './logger';

const axHost = getAxHost();
const axProtocol = getAxProtocol();
const axWsProtocol = getAxWsProtocol();
let refreshingPromise = null;


const customFetch = (uri, options) => {
  refreshingPromise = null;
  const initialRequest = fetch(uri, options);

  return initialRequest.then(response => (response.text())).then(text => {
    const json = JSON.parse(text);
    if (json && json.reasons && json.reasons[0] && json.reasons[0] == 'Signature has expired.') {
      if (!refreshingPromise) {
        const { accessToken } = store.state;
        const { refreshToken } = store.state;
        const address = `${axProtocol}://${axHost}/api/auth/refresh`;

        // Execute the re-authorization request and set the promise returned to this.refreshingPromise
        refreshingPromise = fetch(
          address, {
            method: 'POST',
            headers: {
              Accept: 'application/json',
              'Content-Type': 'application/json',
              Authorization: `Bearer ${accessToken}`
            },
            body: JSON.stringify({
              refresh_token: refreshToken,
              deviceGuid: window.axDeviceGuid
            })
          }
        )
          .then(refresh_token_repsonse => {
            // console.log(refresh_token_repsonse);
            if (refresh_token_repsonse.ok) {
              return refresh_token_repsonse.json().then(refreshJSON => {
                console.log('Refresh token used. New access token recieved.');

                // Return the new access token as a result of the promise
                store.commit('setTokens', {
                  access: refreshJSON.access_token,
                  refresh: refreshJSON.refresh_token
                });
                return refreshJSON.access_token;
              });
            }
            // If the re-authorization request fails, handle it here
            console.log('re-authorization request fails');
            store.dispatch('logOut');
          }).catch(error => {
            console.log(`Re-authorization request fails => ${error}`);
            setTimeout(() => {
              store.dispatch('logOut');
            }, 1000);
          });
      }
      return refreshingPromise.then(newAccessToken => {
        // Now that the refreshing promise has been executed, set it to null
        refreshingPromise = null;

        // Set the authorization header on the original options parameter to the new access token we got
        options.headers.authorization = `Bearer ${newAccessToken}`;
        // Return the promise from the new fetch (which should now have used an active access token)
        // If the initialRequest had errors, this fetch that is returned below is the final result.
        return fetch(uri, options);
      });
    }
    // If there were no errors in the initialRequest, we need to repackage the promise and return it as the final result.
    const result = {};
    result.ok = true;
    result.text = () => new Promise(((resolve, reject) => {
      resolve(text);
    }));
    return result;
  });
};


const httpLink = new HttpLink({
  uri: `${axProtocol}://${axHost}/api/graphql`,
  fetch: customFetch
});

const wsLink = new WebSocketLink({
  uri: `${axWsProtocol}://${axHost}/api/subscriptions`,
  options: {
    reconnect: true
  }
});

const authLink = setContext((_, { headers }) => {
  const token = store.state.accessToken;
  // console.log(`accessToken = ${token}`);
  // return the headers to the context so httpLink can read them
  if (!token) return { headers };
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : ''
    }
  };
});

const link = split(
  ({ query }) => {
    const { kind, operation } = getMainDefinition(query);
    return kind === 'OperationDefinition' && operation === 'subscription';
  },
  wsLink,
  httpLink
);

const auLink = authLink.concat(link);

const cache = new InMemoryCache();
const apolloClient = new ApolloClient({ link: auLink, cache });


export default apolloClient;
