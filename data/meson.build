appstream_file = configure_file(
  input:  'application_id.appdata.xml.in',
  output: application_id + '.appdata.xml',
  configuration: conf,
  install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util,
    args: ['validate', appstream_file]
  )
endif

desktop_file = configure_file(
  input:  'application_id.desktop.in',
  output: application_id + '.desktop',
  configuration: conf,
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

configure_file(
  input:  'application_id.gschema.xml.in',
  output: application_id + '.gschema.xml',
  configuration: conf,
  install: true,
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif

install_subdir(
  'icons/hicolor',
  install_dir: join_paths(get_option('datadir'), 'icons')
)