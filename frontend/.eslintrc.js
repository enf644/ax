module.exports = {
  "root": true,
  "env": {
    "node": true
  },
  "extends": [
    "plugin:vue/essential",
    "@vue/airbnb"
  ],
  "rules": {
    "linebreak-style": 0,
    "singleQuotes": true,
    "comma-dangle": ["error", "never"],
    'import/no-unresolved': "off",
    'import/extensions': "off",
    'import/order':  "off",
    "import/no-extraneous-dependencies": "off"
  },
  "parserOptions": {
    "parser": "babel-eslint"
  }
};
