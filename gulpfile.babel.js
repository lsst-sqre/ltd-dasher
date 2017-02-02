import gulp from 'gulp';
import express from 'express';
import browserSync from 'browser-sync';
import sass from 'gulp-sass';
import autoprefixer from 'gulp-autoprefixer';
import minifyCss from 'gulp-minify-css';
import sourcemaps from 'gulp-sourcemaps';
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
  assetsDeploy: 'app/dashboard/assets',
  assetsDev: '_build/_dasher-assets',
  dev: '_build',
};

// sass modules installed via npm; these are added to node-sass's search paths.
const sassIncludes = [
  'node_modules/normalize-scss/sass'
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

// Runs run.py render to create development HTML in _build
gulp.task('html', () => {
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

gulp.task('default', ['html', 'scss', 'watch', 'server']);
