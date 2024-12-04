hicolor_dir = get_option('datadir') / 'icons/hicolor'

if not get_option('debug')
  install_data('io.github.realmazharhussain.GdmSettings.svg',
    install_dir: hicolor_dir/'scalable/apps',
  )
else
  install_data('io.github.realmazharhussain.GdmSettings.Devel.svg',
    install_dir: hicolor_dir/'scalable/apps',
         rename: 'io.github.realmazharhussain.GdmSettings.svg'
  )
endif

install_data('io.github.realmazharhussain.GdmSettings-symbolic.svg',
  install_dir: hicolor_dir/'symbolic/apps',
)
