const path = require('path');
const ExtractTextPlugin = require("extract-text-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CleanWebpackPlugin = require("clean-webpack-plugin");

module.exports = {
  entry: {
    app:'./app/www/app.js',
    login: './app/www/login.js',
  },
  output: {
    path: path.resolve('app/www/dist'),
    filename: '[name].[hash].bundle.js',
    publicPath:'/'
  },
  module: {
    rules: [
      { 
        test: /\.scss$/,
        use: ExtractTextPlugin.extract({
            fallback: "style-loader",
            use: [
                { loader: "css-loader" },
                { loader: "sass-loader" }
            ]
        })
    },
    {
        test: /\.(png|jpg|jpeg|svg)$/,
        use: [{loader: "file-loader"}]
    },
    {
        test: /\.(js|jsx)?$/,
        exclude: /node_modules/,
        use: "babel-loader"
      }
    ]
  },
  plugins: [
    new ExtractTextPlugin('[name].[contenthash].style.css'),
    new CleanWebpackPlugin(['app/www/dist'], {watch: true}),
    new HtmlWebpackPlugin({
      minify: true,
      title: 'Home - Marble',
      filename: '../templates/app.html',
      template:"./app/www/template.html",
      chunks:['app']
    }),
    new HtmlWebpackPlugin({
      minify: true,
      title: 'Login - Marble',
      template:"./app/www/template.html",
      filename: '../templates/login.html',
      chunks:['login']
    }),
    
  ]
}