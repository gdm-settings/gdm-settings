appstream_file = i18n.merge_file(
        input: 'gdm-settings.metainfo.xml',
       output: app_id + '.metainfo.xml',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'metainfo',
)

appstreamcli = find_program('appstreamcli', required: false)
if appstreamcli.found()
  test(
    'Validate appstream file (with appstreamcli)',
    appstreamcli,
    args: ['validate', '--no-net', appstream_file]
  )
endif

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test(
    'Validate appstream file (with appstream-util)',
    appstream_util,
    args: ['validate', '--nonet', appstream_file]
  )
endif

desktop_file = i18n.merge_file(
        input: 'gdm-settings.desktop',
       output: app_id + '.desktop',
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
          input: 'gdm-settings.service.in',
         output: app_id + '.service',
        install: true,
    install_dir: get_option('datadir') / 'dbus-1/services',
  configuration: configuration_data({
    'bindir': get_option('prefix') / get_option('bindir'),
  }),
)

subdir('gschemas')
subdir('icons')
