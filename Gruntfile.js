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
    cssmin: {
      minify: {
        expand: true,
        cwd: 'jayhawkschedule/static/css/',
        src: ['*.css', '!*.min.css'],
        dest: 'jayhawkschedule/static/css',
        ext: '.min.css'
      }
    },
    concat: {
      options: {
        separator: ';'
      },
      dist: {
        src: ['js/*.js'],
        dest: 'jayhawkschedule/static/js/scripts.js'
      }
    },
    uglify: {
      dist: {
        files: {
          'jayhawkschedule/static/js/scripts.min.js': ['<%= concat.dist.dest %>']
        }
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-compass');
  grunt.loadNpmTasks('grunt-combine-media-queries');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');

  grunt.registerTask('default', ['compass', 'cssmin', 'concat', 'uglify']);

};