"""
create_version_info.py
Genera el archivo version_info.txt para PyInstaller basado en version.py.
"""
import sys
from version import __version__, APP_NAME, APP_PUBLISHER

def create_info():
    # Convert "0.5.0" to (0, 5, 0, 0)
    parts = __version__.split(".")
    while len(parts) < 4:
        parts.append("0")
    version_tuple = tuple(map(int, parts))
    version_str = f"{version_tuple[0]}.{version_tuple[1]}.{version_tuple[2]}.{version_tuple[3]}"

    content = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', '{APP_PUBLISHER}'),
        StringStruct('FileDescription', '{APP_NAME}'),
        StringStruct('FileVersion', '{version_str}'),
        StringStruct('InternalName', '{APP_NAME}'),
        StringStruct('LegalCopyright', 'Copyright (c) {APP_PUBLISHER}'),
        StringStruct('OriginalFilename', '{APP_NAME}.exe'),
        StringStruct('ProductName', '{APP_NAME}'),
        StringStruct('ProductVersion', '{version_str}')])
      ]), 
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    with open("version_info.txt", "w") as f:
        f.write(content)

if __name__ == "__main__":
    create_info()
