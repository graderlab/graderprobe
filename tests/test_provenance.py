import re

from graderprobe import provenance
from graderprobe._provenance import BUILD_SERIAL, install_id

_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def test_provenance_format():
    marker = provenance()
    assert marker.startswith("graderprobe-stamp:")
    assert _UUID.match(marker.split(":", 1)[1])


def test_provenance_uses_install_id():
    assert provenance() == f"graderprobe-stamp:{install_id}"


def test_build_serial_present():
    assert isinstance(BUILD_SERIAL, str)
    assert BUILD_SERIAL.strip()
