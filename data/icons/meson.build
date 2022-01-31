hicolor_dir = join_paths(get_option('datadir'), 'icons/hicolor')

configure_file(
  input: 'scalable/apps/application_id.svg',
  output: application_id + '.svg',
  copy: true,
  install: true,
  install_dir: join_paths(hicolor_dir, 'scalable/apps'),
  )

configure_file(
  input: 'symbolic/apps/application_id-symbolic.svg',
  output: application_id + '-symbolic.svg',
  copy: true,
  install: true,
  install_dir: join_paths(hicolor_dir, 'symbolic/apps'),
  )
