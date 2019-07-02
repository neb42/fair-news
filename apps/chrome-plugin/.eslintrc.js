module.exports = {
  env: {
    browser: true,
    es6: true,
    jest: true,
  },
  parser: 'babel-eslint',
  extends: [
    'airbnb',
    'plugin:flowtype/recommended',
    'plugin:react/recommended',
    'plugin:prettier/recommended',
    'prettier/react',
    'prettier/flowtype',
  ],
  'settings': {
    'import/resolver': {
      'node': {
        'paths': ['app'],
      },
    },
  },
  globals: {
    Atomics: 'readonly',
    SharedArrayBuffer: 'readonly',
  },
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 2018,
    sourceType: 'module',
  },
  plugins: ['react', 'flowtype', 'jest', 'prettier'],
  rules: {
    'comma-dangle': [
      'error',
      'always-multiline',
    ],
    'no-await-in-loop': [0],
    quotes: ['error', 'single', { avoidEscape: true }],
    'object-curly-spacing': ['error', 'always'],
    'react/jsx-filename-extension': [1, { extensions: ['.js'] }],
    'import/order': [
      'error',
      { 
        groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
        'newlines-between': 'always',
      },
    ],
    'max-len': ['error', { code: 100, tabWidth: 2 }],
    'no-plusplus': ['error', { 'allowForLoopAfterthoughts': true }],
    'react/no-array-index-key': 'off',
    'react/sort-comp': ['error', { order: [
      '/props/',
      '/state/',
      'everything-else',
      'instance-variables',
      'static-methods',
      'lifecycle',
      'getters',
      'setters',
      'instance-methods',
      'render',
    ]}],
    // TODO remove after styled component import test issue is fixed
    'import/extensions': ['never'],
    // Disable eslint-plugin-jsx-a11y
    ...Object.keys(require('eslint-plugin-jsx-a11y').rules).reduce((acc, cur) => {
      acc[`jsx-a11y/${cur}`] = 'off'; 
      return acc;
    }, {}),
  },
};
