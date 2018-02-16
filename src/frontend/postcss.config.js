const DEVELOPMENT = (process.env.NODE_ENV || 'development') === 'development';
if (DEVELOPMENT === true) {
  module.exports = {
    plugins: [
      require("postcss-import")(),
      require('autoprefixer')(),
      require('postcss-flexbugs-fixes')(),
    ]
  }
} else {
  module.exports = {
    plugins: [
      require("postcss-import")(),
      require('autoprefixer')({browsers: ['last 9 versions']}),
      require('postcss-flexbugs-fixes')(),
      require('cssnano')({discardComments: {removeAll: true}})
    ]
  }
}
