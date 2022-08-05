gschema_files = [
  'io.github.realmazharhussain.GdmSettings.gschema.xml',
  'io.github.realmazharhussain.GdmSettings.appearance.gschema.xml',
  'io.github.realmazharhussain.GdmSettings.fonts.gschema.xml',
  'io.github.realmazharhussain.GdmSettings.misc.gschema.xml',
  'io.github.realmazharhussain.GdmSettings.night-light.gschema.xml',
  'io.github.realmazharhussain.GdmSettings.sound.gschema.xml',
  'io.github.realmazharhussain.GdmSettings.top-bar.gschema.xml',
  'io.github.realmazharhussain.GdmSettings.pointing.gschema.xml',
  'io.github.realmazharhussain.GdmSettings.pointing.mouse.gschema.xml',
  'io.github.realmazharhussain.GdmSettings.pointing.touchpad.gschema.xml',
  'io.github.realmazharhussain.GdmSettings.tools.gschema.xml',
  'io.github.realmazharhussain.GdmSettings.window-state.gschema.xml',
]
install_data(gschema_files,
  install_dir: get_option('datadir') / 'glib-2.0/schemas',
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test(
    'Validate schema files',
    compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif
