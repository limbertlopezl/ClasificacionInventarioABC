const webpack = require('webpack');
const path = require('path');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const extractSass = new ExtractTextPlugin({
  filename: 'css/[name].css',
  allChunks: true
});
const extractCss = new ExtractTextPlugin({
  filename: 'css/[name].vendors.css',
  allChunks: true
});

const config = {
  context: path.resolve(__dirname),
  target: 'web',
  entry: {
    main: [path.resolve('app/main.jsx')],
  },
  resolve: {
    extensions: ['.js', '.jsx', '.json'],
    modules: [
      path.resolve(__dirname, "app"),
      "node_modules",
    ]
  },
  output: {
    path: path.resolve(__dirname, "static"),
    publicPath: "/static/",
    filename: '[name].js',
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        include: [path.resolve(__dirname, "app")],
        use: [{loader: 'babel-loader'}],
        exclude: /node_modules/
      },
      {
        test: /\.scss$/,
        use: extractSass.extract({
          fallback: "style-loader",
          use: [
            {loader: "css-loader"},
            {loader: "postcss-loader"},
            {loader: "sass-loader"},
          ]
        })
      },
      {
        test: /\.css$/,
        use: extractCss.extract({
          fallback: "style-loader",
          use: [
            {loader: "css-loader"},
            {loader: "postcss-loader"},
          ]
        })
      },
      {
        test: /\.woff(2)?(\?v=\d+\.\d+\.\d+)?$/,
        loader: "url-loader?limit=10000&mimetype=application/font-woff&name=fonts/[name].[ext]&publicPath=../"
      },
      {
        test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/,
        loader: "url-loader?limit=10000&mimetype=application/octet-stream&name=fonts/[name].[ext]&publicPath=../"
      },
      {
        test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
        loader: "file-loader?name=fonts/[name].[ext]&publicPath=../"
      },
      {
        test: /\.(gif|jpg|png|ico)(\?v=\d+\.\d+\.\d+)?$/,
        loader: "file-loader?name=images/[name].[ext]&publicPath=../"
      },
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        loader: "url-loader?limit=10000&mimetype=image/svg+xml&name=images/[name].[ext]&publicPath=../"
      }
    ]
  },
  plugins: [
    extractSass,
    extractCss,
    new webpack.ProvidePlugin({
      '$': 'jquery',
      '_': 'lodash',
      'jQuery': 'jquery',
      'window.jQuery': 'jquery'
    })
  ]
};


module.exports = config;

/*
module.exports = {
  development: Object.assign({}, config, {

    plugins: config.plugins.concat([
      new webpack.DefinePlugin({'__DEV__': true})
    ])
  }),
  production: Object.assign({}, config, {
    plugins: config.plugins.concat([
      new webpack.DefinePlugin({
        '__DEV__': false,
        'process.env.NODE_ENV': JSON.stringify('production')
      }),
      new webpack.optimize.UglifyJsPlugin({
        mangle: true,
        sourcemap: false,
        comments: false,
        compress: {warnings: false}
      })
    ])
  })
};
*/
