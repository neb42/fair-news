module.exports = function (api) {
  api.cache(true);
  return {
    sourceMaps: true,
    presets: [
      '@babel/preset-env',
      '@babel/preset-react',
    ],
    plugins: [
      '@babel/plugin-transform-flow-strip-types',
      '@babel/plugin-proposal-class-properties',
      '@babel/plugin-transform-runtime',
      '@babel/plugin-proposal-object-rest-spread',
    ],
  };
};
