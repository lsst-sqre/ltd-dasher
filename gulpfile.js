const gulp = require('gulp');
const express = require('express');
const browserSync = require('browser-sync');
const sass = require('gulp-sass');
const autoprefixer = require('gulp-autoprefixer');
const cleanCss = require('gulp-clean-css');
const sourcemaps = require('gulp-sourcemaps');
const svgstore = require('gulp-svgstore');
const svgmin = require('gulp-svgmin');
const cheerio = require('gulp-cheerio');
const path = require('path');
const rename = require('gulp-rename');
const noop = require('gulp-noop');
const minimist = require('minimist');
const run = require('gulp-run');

// development express server
var server;

// parse command line options
// --env [dev, deploy]
const options = minimist(process.argv);
const env = options.env || 'dev';

const dirs = {
  scss: 'src/scss',
  svg: 'src/svg',
  icons: 'src/icons',
  assetsDeploy: 'app/dashboard/assets',
  templates: 'app/dashboard/templates',
  assetsDev: '_build/_dasher-assets',
  dev: '_build',
};

// sass modules installed via npm; these are added to node-sass's search paths.
const sassIncludes = ['node_modules'];

// force page reload
function reload() {
  if (server) {
    return browserSync.reload({ stream: true });
  }

  return noop();
}

function hello() {
  console.log('Hello gulp!');
  return Promise.resolve();
}

exports.hello = hello;

function environment() {
  console.log(`${env}`);
  return Promise.resolve();
}

exports.environment = environment;

function scss() {
  return gulp
    .src(`${dirs.scss}/app.scss`)
    .pipe(env === 'dev' ? sourcemaps.init() : noop())
    .pipe(sass.sync({ includePaths: sassIncludes }).on('error', sass.logError))
    .pipe(autoprefixer())
    .pipe(env === 'dev' ? sourcemaps.write() : noop())
    .pipe(env === 'deploy' ? cleanCss() : noop())
    .pipe(env === 'dev' ? gulp.dest(dirs.assetsDev) : noop())
    .pipe(env === 'deploy' ? gulp.dest(dirs.assetsDeploy) : noop())
    .pipe(reload());
}

exports.scss = scss;

function svg() {
  return gulp
    .src(`${dirs.svg}/lsst_underline_logo.svg`)
    .pipe(env === 'dev' ? gulp.dest(`${dirs.assetsDev}`) : noop())
    .pipe(env === 'deploy' ? gulp.dest(`${dirs.assetsDeploy}`) : noop())
    .pipe(reload());
}

exports.svg = svg;

function icons() {
  return gulp
    .src(`${dirs.icons}/**/*.svg`, { base: dirs.icons })
    .pipe(
      rename(function(file) {
        var name = file.dirname.split(path.sep);
        name.push(file.basename);
        file.basename = name.join('-');
      })
    )
    .pipe(
      cheerio({
        run: function($) {
          $('[fill]').removeAttr('fill');
          // for JIRA icon
          $('.st0').removeClass('st0');
        },
        parserOptions: { xmlMode: true },
      })
    )
    .pipe(svgmin())
    .pipe(svgstore({ inlineSvg: true }))
    .pipe(gulp.dest(`${dirs.templates}`));
}

exports.icons = icons;

// Runs run.py render to create development HTML in _build
function html() {
  return run('python run.py render')
    .exec()
    .pipe(gulp.dest(`${dirs.dev}/logs`)) // makes the reload synchronous
    .pipe(reload());
}

exports.html = gulp.series(icons, html);

function server() {
  server = express();
  server.use(express.static(dirs.dev));
  server.listen(8000);
  browserSync({ proxy: 'localhost:8000' });
}

exports.server = server;

// make all assets needed for the docker image
const assets = gulp.parallel(scss, svg, icons);
exports.assets = assets;

function watcher() {
  gulp.watch(
    [`${dirs.scss}/**/*.scss`, `app/dashboard/**/*.{scss,jinja}`],
    {},
    gulp.series(assets, html)
  );
}

exports.default = gulp.parallel(server, watcher);
