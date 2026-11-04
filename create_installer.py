"""
create_installer.py
Genera el script Inno Setup (installer.iss) con la configuración por usuario
y el menú contextual.
"""
import os
from version import __version__, APP_NAME, APP_PUBLISHER

EXT_MENUS = {
    "pdf": [
        ("open", "Abrir en PDF Master"),
        ("pdf2img", "Convertir a Imágenes"),
        ("merge", "Unir con..."),
        ("reorder", "Reordenar páginas"),
        ("repair", "Reparar PDF"),
    ],
    "jpg":  [("open", "Abrir en PDF Master"), ("img2pdf", "Convertir a PDF")],
    "jpeg": [("open", "Abrir en PDF Master"), ("img2pdf", "Convertir a PDF")],
    "png":  [("open", "Abrir en PDF Master"), ("img2pdf", "Convertir a PDF")],
    "bmp":  [("open", "Abrir en PDF Master"), ("img2pdf", "Convertir a PDF")],
    "tiff": [("open", "Abrir en PDF Master"), ("img2pdf", "Convertir a PDF")],
    "webp": [("open", "Abrir en PDF Master"), ("img2pdf", "Convertir a PDF")],
}

# FIJO: no cambiar nunca. Permite que una versión nueva actualice la instalada.
# (En Inno Setup la llave inicial se escapa duplicándola: "{{")
APP_ID = "{{8F3C2A71-5D4E-4B9A-9C61-2E7F0A1D4B35}"

EXE = f"{{app}}\\{APP_NAME}.exe"


def generate_iss() -> None:
    os.makedirs("installer/Output", exist_ok=True)
    lines = [
        "[Setup]",
        f"AppId={APP_ID}",
        f"AppName={APP_NAME}",
        f"AppVersion={__version__}",
        f"AppVerName={APP_NAME} {__version__}",
        f"AppPublisher={APP_PUBLISHER}",
        f"DefaultDirName={{localappdata}}\\Programs\\{APP_NAME}",
        "UsePreviousAppDir=yes",
        "UsePreviousTasks=yes",
        "PrivilegesRequired=lowest",
        "OutputDir=installer\\Output",
        f"OutputBaseFilename=PDF-Master-Setup-{__version__}",
        "SetupIconFile=assets\\icon.ico",
        f"UninstallDisplayIcon={EXE}",
        "Compression=lzma2",
        "SolidCompression=yes",
        "DisableProgramGroupPage=yes",
        "CloseApplications=force",
        "RestartApplications=no",
        "ChangesAssociations=yes",
        f"VersionInfoVersion={__version__}",
        "",
        "[Languages]",
        'Name: "spanish"; MessagesFile: "compiler:Languages\\Spanish.isl"',
        "",
        "[Tasks]",
        'Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; Flags: unchecked',
        'Name: "contextmenu"; Description: "Agregar PDF Master al menú contextual del Explorador"',
        "",
        "[Files]",
        f'Source: "dist\\{APP_NAME}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs',
        "",
        "[Icons]",
        f'Name: "{{autoprograms}}\\{APP_NAME}"; Filename: "{EXE}"',
        f'Name: "{{autodesktop}}\\{APP_NAME}"; Filename: "{EXE}"; Tasks: desktopicon',
        "",
        "[Run]",
        f'Filename: "{EXE}"; Description: "Abrir {APP_NAME}"; Flags: nowait postinstall skipifsilent',
        "",
        "[Registry]",
    ]

    # Menú contextual en HKCU (no requiere Administrador)
    t = "Tasks: contextmenu"
    for ext, items in EXT_MENUS.items():
        base = f"Software\\Classes\\SystemFileAssociations\\.{ext}\\shell\\PDFMaster"
        lines.append(f"; .{ext}")
        lines.append(f'Root: HKCU; Subkey: "{base}"; ValueType: string; ValueName: "MUIVerb"; ValueData: "{APP_NAME}"; Flags: uninsdeletekey; {t}')
        lines.append(f'Root: HKCU; Subkey: "{base}"; ValueType: string; ValueName: "Icon"; ValueData: """{EXE}"""; {t}')
        lines.append(f'Root: HKCU; Subkey: "{base}"; ValueType: string; ValueName: "SubCommands"; ValueData: ""; {t}')
        for tool_id, label in items:
            item = f"{base}\\shell\\{tool_id}"
            lines.append(f'Root: HKCU; Subkey: "{item}"; ValueType: string; ValueData: "{label}"; {t}')
            # Mantiene la opción visible al seleccionar más de 15 archivos
            lines.append(f'Root: HKCU; Subkey: "{item}"; ValueType: string; ValueName: "MultiSelectModel"; ValueData: "Player"; {t}')
            lines.append(f'Root: HKCU; Subkey: "{item}\\command"; ValueType: string; ValueData: """{EXE}"" --tool {tool_id} ""%1"""; {t}')
        lines.append("")

    # Al desinstalar: preguntar si se borra la configuración del usuario
    lines += [
        "[Code]",
        "procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);",
        "begin",
        "  if CurUninstallStep = usPostUninstall then",
        f"    if MsgBox('¿Deseas borrar también tu configuración de {APP_NAME}?', mbConfirmation, MB_YESNO) = IDYES then",
        f"      DelTree(ExpandConstant('{{userappdata}}\\{APP_NAME}'), True, True, True);",
        "end;",
        "",
    ]

    # UTF-8 con BOM para que Inno Setup lea bien las tildes
    with open("installer.iss", "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines))

    print("installer.iss generado correctamente.")


if __name__ == "__main__":
    generate_iss()
