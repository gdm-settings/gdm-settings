#blueprint_compiler = generator(
#  find_program('blueprint-compiler'),
#  output: '@BASENAME@.ui', #.replace('.blp', '.ui'),
#  arguments: ['compile', '@INPUT@', '--output', '@OUTPUT@'],
#)

main_window_blp = configure_file(
  input:  'main-window.blp.in',
  output: 'main-window.blp',
  configuration: conf,
  install: false,
)

blueprints = [main_window_blp] + files(
  'appearance-page.blp',
  'fonts-page.blp',
  'night-light-page.blp',
  'sound-page.blp',
  'top-bar-page.blp',
  'touchpad-page.blp',
  'misc-page.blp',
)

custom_target('ui_files',
  input: blueprints,
  output: project_name,
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@INPUT@'],
  install: true,
  install_dir: datadir,
)

install_data(files('image-chooser.ui'), install_dir: pkgdatadir)

#ui_files = blueprint_compiler.process(blueprints)

#custom_target('ui_files',
#  input: ui_files,
#  output: project_name,
#  command: [find_program('install'), '-Dm644', '-t', '@OUTPUT@', '@INPUT@'],
#  install: true,
#  install_dir: datadir,
#)
