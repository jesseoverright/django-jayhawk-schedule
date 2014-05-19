module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    compass: {
      dist: {
        options: {
          config: 'config.rb'
        }
      }
    },
    cmq: {
      options: {
        log: false
      },
      your_target: {
        files: {
          'jayhawkschedule/static/css': ['sass/compiled/*.css']
        }
      }
    },
    cssmin: {
      minify: {
        expand: true,
        cwd: 'jayhawkschedule/static/css/',
        src: ['*.css', '!*.min.css'],
        dest: 'jayhawkschedule/static/css',
        ext: '.min.css'
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-compass');
  grunt.loadNpmTasks('grunt-combine-media-queries');
  grunt.loadNpmTasks('grunt-contrib-cssmin');

  grunt.registerTask('default', ['compass', 'cmq', 'cssmin']);

};