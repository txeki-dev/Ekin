"""LICENSE oficial de PolyForm Noncommercial y avisos de terceros que viajan con el instalador."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

POLYFORM_NC_SECTIONS = [
    "Acceptance", "Copyright License", "Distribution License", "Notices",
    "Changes and New Works License", "Patent License", "Noncommercial Purposes", "Personal Uses",
    "Noncommercial Organizations", "Fair Use", "No Other Rights", "Patent Defense", "Violations",
    "No Liability", "Definitions",
]


def test_license_is_the_official_polyform_noncommercial_text():
    """El LICENSE tenía 10 de las 15 secciones de PolyForm Noncommercial 1.0.0 y un descargo al
    estilo MIT. Ahora es el texto oficial, con la línea `Required Notice:` que la licencia obliga
    a conservar al redistribuir."""
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert re.findall(r"^## (.+)$", text, re.M) == POLYFORM_NC_SECTIONS
    assert re.search(r"^Required Notice: Copyright \d{4} .+$", text, re.M)
    assert "within 32 days of receiving notice" in text


def test_installer_ships_license_and_third_party_notices():
    """El instalador no llevaba ni la licencia de Ekin ni las de lo que empaqueta (Qt/PySide6 LGPL,
    Python, Pygments…). LICENSE y THIRD_PARTY_NOTICES.md van a la carpeta de Ekin y los textos de
    licencia a _internal/licenses (el de Python, del intérprete que compila)."""
    iss = (ROOT / "installer.iss").read_text(encoding="utf-8")
    files = iss.split("[Files]", 1)[1].split("[Icons]", 1)[0]
    for name in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
        assert f'Source: "{name}"; DestDir: "{{app}}"' in files
    spec = (ROOT / "ekin.spec").read_text(encoding="utf-8")
    assert '("licenses", "licenses")' in spec
    assert 'os.path.join(sys.base_prefix, "LICENSE.txt")' in spec


def test_third_party_notices_link_to_files_that_exist():
    notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    links = re.findall(r"\]\(((?:licenses|assets)/[^)]+)\)", notices)
    assert len(links) >= 6
    for link in links:
        assert (ROOT / link).is_file(), link
