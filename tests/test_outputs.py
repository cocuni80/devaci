import json
import xml.dom.minidom
from pathlib import Path

import pytest

from devaci import DeployClass

REPO = Path(__file__).resolve().parent.parent
XLSX = REPO / "data" / "IBKACI6_v2.2_jriveros.xlsx"
TEMPLATE = REPO / "data" / "templates" / "generic_v2.3.j2"

OC = "OC180460"

SETTINGS = {
    "testing": True,
    "filters_source_sheet": "OCs",
    "file_output": f"outputs/scripts/{OC}_config",
    "logging_output": f"outputs/logs/{OC}_logging",
}


@pytest.mark.skipif(not XLSX.exists() or not TEMPLATE.exists(), reason="private data not available")
def test_deploy_outputs():
    aci = DeployClass(working_folder=REPO, **SETTINGS)
    aci.xlsx = "data/IBKACI6_v2.2_jriveros.xlsx"
    aci.template = "data/templates/generic_v2.3.j2"
    aci.deploy()

    # 1. Resultado exitoso
    assert aci.results[0]["success"] is True

    # 2. XML de salida: existe, no vacio, valido y filtrado
    xml_path = REPO / f"outputs/scripts/{OC}_config.xml"
    assert xml_path.exists()
    xml_text = xml_path.read_text(encoding="utf-8")
    assert xml_text.strip()
    xml.dom.minidom.parseString(xml_text)
    assert "Backend_AP" in xml_text
    assert 'name="Interbank"' in xml_text
    assert "OC152069" not in xml_text

    # 3. Logging JSON: lista valida con entradas
    log_path = REPO / f"outputs/logs/{OC}_logging.json"
    assert log_path.exists()
    history = json.loads(log_path.read_text(encoding="utf-8"))
    assert isinstance(history, list) and history
    assert all(isinstance(e, dict) and "success" in e and "log" in e for e in history)
