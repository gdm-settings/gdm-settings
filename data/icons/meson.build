hicolor_dir = data_dir / 'icons/hicolor'

if get_option('buildtype') == 'release'
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
