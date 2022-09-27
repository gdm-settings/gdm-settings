blueprints = files(
  'main-window.blp',
  'appearance-page.blp',
  'fonts-page.blp',
  'display-page.blp',
  'sound-page.blp',
  'top-bar-page.blp',
  'pointing-page.blp',
  'login-screen-page.blp',
  'power-page.blp',
  'tools-page.blp',
)

blueprint_compiler = find_program('blueprint-compiler')

custom_target('ui_files',
        input: blueprints,
       output: meson.project_name(),
      command: [blueprint_compiler, 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
      install: true,
  install_dir: get_option('datadir'),
)
