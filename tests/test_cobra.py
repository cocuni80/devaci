import cobra.model.coop
import cobra.mit.request


def test_cobra_model_coop_available():
    assert hasattr(cobra.model.coop, "Pol")


def test_cobra_mit_request_available():
    assert hasattr(cobra.mit.request, "ConfigRequest")
