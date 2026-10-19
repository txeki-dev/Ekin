# Third-party notices

Ekin Kanban is licensed under the PolyForm Noncommercial License 1.0.0 (see [LICENSE](LICENSE)). The Windows installer also ships the third-party software below, each under its own license. In an installed copy the license texts are in `_internal\licenses\` and, for the fonts and icons, next to them in `_internal\assets\`.

| Component | License | License text | Source |
| --- | --- | --- | --- |
| Python and its standard library, with the libraries bundled in its Windows build (OpenSSL, libffi, SQLite, bzip2, xz, zlib, expat, mpdecimal) | PSF License 2.0, plus the licenses listed in that file | `licenses/Python-LICENSE.txt`, copied from the Python that builds the installer | <https://www.python.org/> |
| Qt 6, PySide6 and Shiboken6 (Qt for Python) | GNU LGPL 3.0 | [licenses/LGPL-3.0.txt](licenses/LGPL-3.0.txt), which adds permissions to [licenses/GPL-3.0.txt](licenses/GPL-3.0.txt) | <https://download.qt.io/official_releases/QtForPython/> and <https://code.qt.io/cgit/pyside/pyside-setup.git/> |
| Pygments | BSD 2-Clause | [licenses/Pygments-LICENSE.txt](licenses/Pygments-LICENSE.txt) and [licenses/Pygments-AUTHORS.txt](licenses/Pygments-AUTHORS.txt) | <https://pygments.org/> |
| Lucide icons (some derived from Feather) | ISC (Feather: MIT) | [assets/icons/lucide/LICENSE](assets/icons/lucide/LICENSE) | <https://lucide.dev/> |
| Figtree font | SIL Open Font License 1.1 | [assets/fonts/Figtree-OFL.txt](assets/fonts/Figtree-OFL.txt) | <https://github.com/erikdkennedy/figtree> |
| Caprasimo font | SIL Open Font License 1.1 | [assets/fonts/Caprasimo-OFL.txt](assets/fonts/Caprasimo-OFL.txt) | <https://github.com/docrepair-fonts/caprasimo-fonts> |
| PyInstaller bootloader (starts `Ekin.exe`) | GNU GPL 2.0 with the bootloader exception, which allows shipping it with programs under any license | <https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt> | <https://pyinstaller.org/> |
| Microsoft Visual C++ runtime (`VCRUNTIME140.dll`, shipped with Python) | Microsoft Distributable Code | `licenses/Python-LICENSE.txt`, section *Additional Conditions for this Windows binary build* | <https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist> |

## Qt for Python (LGPL 3.0)

Ekin uses the Qt and PySide6 libraries unmodified, as the separate files PyInstaller places in `_internal\PySide6\` and `_internal\shiboken6\`. You may replace them with your own builds of the same versions. Their source code is available from the Qt Project at the links above.
