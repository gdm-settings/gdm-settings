gschema_files = [
  'application_id.gschema.xml.in',
  'application_id.appearance.gschema.xml.in',
  'application_id.fonts.gschema.xml.in',
  'application_id.misc.gschema.xml.in',
  'application_id.night-light.gschema.xml.in',
  'application_id.sound.gschema.xml.in',
  'application_id.top-bar.gschema.xml.in',
  'application_id.pointing.gschema.xml.in',
  'application_id.pointing.mouse.gschema.xml.in',
  'application_id.pointing.touchpad.gschema.xml.in',
  'application_id.tools.gschema.xml.in',
  'application_id.window-state.gschema.xml.in',
  ]

foreach gschema_file: gschema_files
  configure_file(
    input:  gschema_file,
    output: gschema_file.replace('application_id', application_id).replace('.in', ''),
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
