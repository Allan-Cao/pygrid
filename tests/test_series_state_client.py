import pytest
import os
from pygrid import GridClient
from dotenv import load_dotenv


@pytest.fixture(scope="module")
def grid_client():
    """Fixture to provide GridClient with API key."""
    if os.getenv("GRID_API_KEY") is None:
        load_dotenv(override=True)

    api_key = os.getenv("GRID_API_KEY")
    assert api_key, "GRID_API_KEY must be set"

    return GridClient(api_key)


def test_get_series_state_legacy(grid_client):
    """Test legacy series state retrieval."""
    result = grid_client.get_series_state("2604952")
    assert result.series_state.id == "2604952"


def test_get_series_state_current(grid_client):
    """Test current series state retrieval."""
    result = grid_client.get_series_state("2816764")
    assert result.series_state.id == "2816764"
