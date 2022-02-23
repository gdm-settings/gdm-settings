appstream_file = configure_file(
  input:  'application_id.appdata.xml.in',
  output: application_id + '.appdata.xml',
  configuration: conf,
  install: true,
  install_dir: datadir / 'metainfo',
)

appstreamcli = find_program('appstreamcli', required: false)
if appstreamcli.found()
  test('Validate appstream file', appstreamcli,
    args: ['validate', '--no-net', '--pedantic', appstream_file]
  )
endif

desktop_file = configure_file(
  input:  'application_id.desktop.in',
  output: application_id + '.desktop',
  configuration: conf,
  install: true,
  install_dir: datadir / 'applications',
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

subdir('gschemas')
subdir('icons')
