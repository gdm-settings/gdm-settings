blueprint_compiler_prog = find_program('blueprint-compiler', required: false)
if not blueprint_compiler_prog.found()
  subproject('blueprint-compiler')
  blueprint_compiler_prog = find_program('blueprint-compiler')
endif

blueprint_compiler = generator(
  blueprint_compiler_prog,
  output: '@BASENAME@.ui', #.replace('.blp', '.ui'),
  arguments: ['compile', '@INPUT@', '--output', '@OUTPUT@'],
)

main_window_blp = configure_file(
  input:  'main-window.blp.in',
  output: 'main-window.blp',
  configuration: conf,
  install: false,
)

blueprints = [main_window_blp] + files(
  'appearance-page.blp',
  'fonts-page.blp',
  'display-page.blp',
  'sound-page.blp',
  'top-bar-page.blp',
  'touchpad-page.blp',
  'misc-page.blp',
  'tools-page.blp',
)

#custom_target('ui_files',
#  input: blueprints,
#  output: project_name,
#  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@INPUT@'],
#  install: true,
#  install_dir: datadir,
#)

ui_files = blueprint_compiler.process(blueprints)

#foreach file: ui_files
#  install_data(file,
#    install_dir: datadir / project_name,
#  )
#endforeach

custom_target('ui_files',
  input: ui_files,
  output: project_name,
  command: [find_program('install'), '-Dm644', '-t', '@OUTPUT@', '@INPUT@'],
  install: true,
  install_dir: datadir,
)
