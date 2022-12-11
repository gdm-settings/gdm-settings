blueprint_compiler = find_program('blueprint-compiler')

blueprint_sources = files(
  'ui/main-window.blp',
  'ui/appearance-page.blp',
  'ui/fonts-page.blp',
  'ui/display-page.blp',
  'ui/sound-page.blp',
  'ui/top-bar-page.blp',
  'ui/pointing-page.blp',
  'ui/login-screen-page.blp',
  'ui/power-page.blp',
  'ui/tools-page.blp',
)

blueprints = custom_target('blueprints',
        input: blueprint_sources,
       output: '.',
      command: [blueprint_compiler, 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('resources', 'gdm-settings.gresource.xml',
           install: true,
       install_dir: get_option('datadir') / meson.project_name(),
      dependencies: blueprints,
  gresource_bundle: true,
)
