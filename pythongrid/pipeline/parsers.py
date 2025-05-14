import re


def parse_tournament_name(tournament: str):
    """
    Parse tournament names with formats:
        league year split
        league year
        league - split year (event_type: details)
    Args:
        tournament: Tournament name string
    Returns:
        Tuple containing (league, year, split, event_type)
    """
    league = None
    year = None
    split = None
    event_type = None

    # Handle bracketed event type
    if "(" in tournament:
        main_part = tournament.split("(")[0].strip()
        event_part = re.search(r"\((.*?):", tournament)
        if event_part:
            event_type = event_part.group(1).strip()
    else:
        main_part = tournament

    # Extract year
    year_match = re.search(r"20\d{2}", main_part)
    if year_match:
        year = year_match.group(0)

        # Handle dash format
        if " - " in main_part:
            parts = main_part.split(" - ", 1)
            if len(parts) > 0:
                league = parts[0].strip() or None

            if len(parts) > 1:
                rest = parts[1]
                split_match = re.search(r"(\w+)\s+" + year, rest)
                if split_match:
                    split = split_match.group(1)
        else:
            parts = main_part.split(year)
            if len(parts) > 0:
                league = parts[0].strip() or None
            if len(parts) > 1:
                split = parts[1].strip() or None

    return (league, year, split, event_type)


def tournament_from_grid(tournament_data):
    """
    Convert GRID tournament data to dictionary format.

    Args:
        tournament_data: Tournament data from GRID API

    Returns:
        Dictionary with tournament details
    """
    logo_url = None
    if hasattr(tournament_data, "logo_url"):
        logo_url = (
            None
            if tournament_data.logo_url
            == "https://cdn.grid.gg/assets/tournament-logos/generic"
            else tournament_data.logo_url
        )

    league, year, split, event_type = parse_tournament_name(tournament_data.name)

    external_ids = {}
    if hasattr(tournament_data, "external_links"):
        external_ids = {
            _.data_provider.name: _.external_entity.id
            for _ in tournament_data.external_links
        }

    tournament_details = {
        "id": int(tournament_data.id),
        "name": tournament_data.name,
        "league": league,
        "year": year,
        "split": split,
        "event_type": event_type,
        "start_date": getattr(tournament_data, "start_date", None),
        "end_date": getattr(tournament_data, "end_date", None),
        "external_ids": external_ids,
        "additional_details": {
            "name_shortened": getattr(tournament_data, "name_shortened", None),
            "logo_url": logo_url,
        },
    }

    return tournament_details
