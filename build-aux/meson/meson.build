postinstall_py = configure_file(
         input: 'postinstall.py.in',
        output: '@BASENAME@',
 configuration: conf,
 )

meson.add_install_script(postinstall_py)
