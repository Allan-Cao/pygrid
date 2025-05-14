import pytest
from pythongrid.pipeline import parse_tournament_name


@pytest.mark.parametrize(
    "tournament_name,expected_result",
    [
        ("LEC 2023 Spring", ("LEC", "2023", "Spring", None)),
        ("LCK 2024 Summer", ("LCK", "2024", "Summer", None)),
        ("LPL 2025 (Qualifiers: Group Stage)", ("LPL", "2025", None, "Qualifiers")),
        (
            "Worlds - 2023 (Play In Groups: Group B)",
            ("Worlds", "2023", None, "Play In Groups"),
        ),
        (
            "CBLOL Academy - Split 1 2024 (Regular Season: Groups)",
            ("CBLOL Academy", "2024", "1", "Regular Season"),
        ),
        (
            "Arabian League - Winter 2025 (Playoffs: Playoffs)",
            ("Arabian League", "2025", "Winter", "Playoffs"),
        ),
        ("Invalid Tournament Format", (None, None, None, None)),
        ("No Year Tournament", (None, None, None, None)),
    ],
)
def test_parse_tournament_name(tournament_name, expected_result):
    assert parse_tournament_name(tournament_name) == expected_result
