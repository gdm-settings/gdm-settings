appstream_file = i18n.merge_file(
        input: 'io.github.realmazharhussain.GdmSettings.metainfo.xml.in',
       output: '@BASENAME@',
       po_dir: '../po',
      install: true,
  install_dir: data_dir/'metainfo',
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test(
    'Validate appstream file',
    appstream_util,
    args: ['validate-relax', '--nonet', appstream_file]
  )
endif

desktop_file = i18n.merge_file(
        input: 'io.github.realmazharhussain.GdmSettings.desktop.in',
       output: '@BASENAME@',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: data_dir / 'applications',
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test(
    'Validate desktop file',
    desktop_utils,
    args: [desktop_file]
  )
endif

subdir('gschemas')
subdir('icons')
