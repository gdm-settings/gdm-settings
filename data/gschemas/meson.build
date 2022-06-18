gschema_files = [
  'io.github.realmazharhussain.GdmSettings.gschema.xml.in',
  'io.github.realmazharhussain.GdmSettings.appearance.gschema.xml.in',
  'io.github.realmazharhussain.GdmSettings.fonts.gschema.xml.in',
  'io.github.realmazharhussain.GdmSettings.misc.gschema.xml.in',
  'io.github.realmazharhussain.GdmSettings.night-light.gschema.xml.in',
  'io.github.realmazharhussain.GdmSettings.sound.gschema.xml.in',
  'io.github.realmazharhussain.GdmSettings.top-bar.gschema.xml.in',
  'io.github.realmazharhussain.GdmSettings.pointing.gschema.xml.in',
  'io.github.realmazharhussain.GdmSettings.pointing.mouse.gschema.xml.in',
  'io.github.realmazharhussain.GdmSettings.pointing.touchpad.gschema.xml.in',
  'io.github.realmazharhussain.GdmSettings.tools.gschema.xml.in',
  'io.github.realmazharhussain.GdmSettings.window-state.gschema.xml.in',
  ]

foreach gschema_file: gschema_files
  configure_file(
    input:  gschema_file,
    output: '@BASENAME@',
    configuration: conf,
    install: true,
    install_dir: data_dir / 'glib-2.0/schemas',
  )
endforeach

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema files', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif
