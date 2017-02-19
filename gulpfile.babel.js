import gulp from 'gulp';
import express from 'express';
import browserSync from 'browser-sync';
import sass from 'gulp-sass';
import autoprefixer from 'gulp-autoprefixer';
import minifyCss from 'gulp-minify-css';
import sourcemaps from 'gulp-sourcemaps';
var svgstore = require('gulp-svgstore');
var svgmin = require('gulp-svgmin');
var cheerio = require('gulp-cheerio');
var path = require('path');
var rename = require('gulp-rename');
var gutil = require('gulp-util');
var minimist = require('minimist');
var run = require('gulp-run');

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
const sassIncludes = [
  'node_modules',
  // 'node_modules/inuitcss',
  // 'node_modules/sass-mq',
  // 'node_modules/normalize-scss/sass',
  // 'node_modules/sass-math-pow/sass/'
];

// force page reload
function reload() {
  if (server) {
    return browserSync.reload({ stream: true });
  }

  return gutil.noop();
}

gulp.task('hello', () => console.log('Hello gulp!'));

gulp.task('environment', () => console.log(`${env}`));

gulp.task('scss', () => {
  return gulp.src(`${dirs.scss}/app.scss`)
    .pipe(env === 'dev' ? sourcemaps.init() : gutil.noop())
    .pipe(sass.sync({ includePaths: sassIncludes }).on('error', sass.logError))
    .pipe(autoprefixer())
    .pipe(env === 'dev' ? sourcemaps.write() : gutil.noop())
    .pipe(env === 'deploy' ? minifyCss() : gutil.noop())
    .pipe(env === 'dev' ? gulp.dest(dirs.assetsDev) : gutil.noop())
    .pipe(env === 'deploy' ? gulp.dest(dirs.assetsDeploy) : gutil.noop())
    .pipe(reload());
});

gulp.task('svg', () => {
  return gulp.src(`${dirs.svg}/lsst_underline_logo.svg`)
    .pipe(env === 'dev' ? gulp.dest(`${dirs.assetsDev}`) : gutil.noop())
    .pipe(env === 'deploy' ? gulp.dest(`${dirs.assetsDeploy}`) : gutil.noop())
    .pipe(reload());
});

gulp.task('icons', function () {
  return gulp
    .src(`${dirs.icons}/**/*.svg`, { base: dirs.icons })
    .pipe(rename(function (file) {
      var name = file.dirname.split(path.sep);
      name.push(file.basename);
      file.basename = name.join('-');
    }))
    .pipe(cheerio({
      run: function ($) {
        $('[fill]').removeAttr('fill');
      },
      parserOptions: { xmlMode: true }
    }))
    .pipe(svgmin())
    .pipe(svgstore({ inlineSvg: true }))
    .pipe(gulp.dest(`${dirs.templates}`));
});

// Runs run.py render to create development HTML in _build
gulp.task('html', ['icons'], () => {
  return run('python run.py render').exec()
    .pipe(gulp.dest(`${dirs.dev}/logs`)) // makes the reload synchronous
    .pipe(reload());
});

gulp.task('server', () => {
  server = express();
  server.use(express.static(dirs.dev));
  server.listen(8000);
  browserSync({ proxy: 'localhost:8000' });
});

gulp.task('watch', () => {
  gulp.watch(`${dirs.scss}/**/*.scss`, ['scss']);
  gulp.watch(`app/dashboard/**/*.{scss,jinja}`, ['html']);
});

gulp.task('default', ['scss', 'svg', 'html', 'watch', 'server']);
