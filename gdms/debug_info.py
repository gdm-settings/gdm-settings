from gdms import VERSION
from gdms import env
from gdms import gresource


debug_info = (
    ("Application Version", VERSION),
    ("Operating System", env.OS_PRETTY_NAME),
    ("Package Type", env.PACKAGE_TYPE.name),
    ("TEMP_DIR", env.TEMP_DIR),
    ("HOST_DATA_DIRS", env.HOST_DATA_DIRS),
    ("Main GResource File", gresource.ShellGresourceFile),
    ("Ubuntu GResource File", gresource.UbuntuGdmGresourceFile),
    ("Default GResource File", gresource.get_default()),
)


__markdown_cache = None

def as_markdown():
    global __markdown_cache

    if __markdown_cache:
        return __markdown_cache

    markdown_lines = []
    for key, val in debug_info:
        markdown_lines.append(f"**{key}**: `{val}`  ")

    __markdown_cache = '\n'.join(markdown_lines)
    return __markdown_cache
