blueprints = files(
  'main-window.blp',
  'app-preferences.blp',
  'appearance-page.blp',
  'fonts-page.blp',
  'display-page.blp',
  'sound-page.blp',
  'top-bar-page.blp',
  'pointing-page.blp',
  'misc-page.blp',
  'tools-page.blp',
)

blueprint_compiler = find_program('blueprint-compiler', required: false)
if not blueprint_compiler.found()
  subproject('blueprint-compiler')
  blueprint_compiler = find_program('blueprint-compiler')
endif

custom_target('ui_files',
        input: blueprints,
       output: project_name,
      command: [blueprint_compiler, 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
      install: true,
  install_dir: data_dir,
)
