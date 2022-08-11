appstream_file = i18n.merge_file(
        input: 'io.github.realmazharhussain.GdmSettings.metainfo.xml.in',
       output: '@BASENAME@',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'metainfo',
)

appstreamcli = find_program('appstreamcli', required: false)
if appstreamcli.found()
  test(
    'Validate appstream file',
    appstreamcli,
    args: ['validate', '--no-net', appstream_file]
  )
endif

desktop_file = i18n.merge_file(
        input: 'io.github.realmazharhussain.GdmSettings.desktop.in',
       output: '@BASENAME@',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'applications',
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test(
    'Validate desktop file',
    desktop_utils,
    args: [desktop_file]
  )
endif

configure_file(
          input: 'io.github.realmazharhussain.GdmSettings.service.in',
         output: 'io.github.realmazharhussain.GdmSettings.service',
        install: true,
    install_dir: get_option('datadir') / 'dbus-1/services',
  configuration: configuration_data({
    'bindir': get_option('prefix') / get_option('bindir'),
  }),
)

subdir('gschemas')
subdir('icons')
