const webpack = require('webpack')
const GenerateJsonPlugin = require('generate-json-webpack-plugin')
const merge = require('webpack-merge')
const path = require('path')

module.exports = function (env) {
  console.log(env)
  const [mode, platform, benchmark, firefoxBeta] = env.split(':')
  let version = require('./manifest/common.json').version
  if (firefoxBeta) version += 'beta'

  const config = {
    entry: {
      background_script: './src/index.js',
    },
    output: {
      path: path.join(__dirname, '/dist'),
      filename: '[name].js',
      sourceMapFilename: '[name].js.map' // always generate source maps
    },
    devtool: 'source-map',
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
          },
        },
      ],
    },
    resolve: {
      modules: ['./src', './node_modules']
    },
    plugins: [
      new webpack.optimize.ModuleConcatenationPlugin(),
      new GenerateJsonPlugin(
        'manifest.json',
        merge(
          require('./manifest/common.json'),
          require(`./manifest/${platform}.json`),
          { version }
        ),
        null,
        2
      )
    ]
  }

  return config
}