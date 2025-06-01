import re
import arrow
from .transformations import process_team_objectives

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
        "id": tournament_data.id,
        "name": tournament_data.name,
        "league": league,
        "year": year,
        "split": split,
        "event_type": event_type,
        "start_date": getattr(tournament_data, "start_date", None),
        "end_date": getattr(tournament_data, "end_date", None),
        "additional_details": {
            "external_ids": external_ids,
            "name_shortened": getattr(tournament_data, "name_shortened", None),
            "logo_url": logo_url,
        },
    }

    return tournament_details

def parse_series_format(series_format: str) -> int | None:
    name_split = series_format.split("best-of-")
    if len(name_split) != 2:
        return None
    return int(name_split[1])
        
def series_from_grid(series_data) -> dict:
    return {
        "id": series_data.node.id,
        "type": series_data.node.type.name,
        "scheduled_start_time": arrow.get(series_data.node.start_time_scheduled).datetime,
        "tournament_id": series_data.node.tournament.id,
        "format": parse_series_format(series_data.node.format.name),
        "external_links": {_.data_provider.name: _.external_entity.id for _ in series_data.node.external_links},
    }

def team_from_grid(team_data):
    logo_url = None if team_data.logo_url == 'https://cdn.grid.gg/assets/team-logos/generic' else team_data.logo_url
    associated_ids = {_.data_provider.name: _.external_entity.id for _ in team_data.external_links}
    associated_ids["GRID"] = team_data.id
    team_details = {
        "id": team_data.id,
        "name": team_data.name,
        "team_code": team_data.name_shortened,
        "source_data": {
            "external_ids": associated_ids,
            "logo_url": logo_url,
            "color_primary": team_data.color_primary,
            "color_secondary": team_data.color_secondary,
        }
    }
    return team_details

def parse_duration(duration: str) -> int:
    m = re.match(r"^PT(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S?)?$", duration)
    
    if not m:
        return 0
    
    hours, minutes, seconds = m.groups()
    
    total_seconds = 0
    if hours:
        total_seconds += float(hours) * 3600
    if minutes:
        total_seconds += float(minutes) * 60
    if seconds:
        total_seconds += float(seconds)
    
    return int(total_seconds)

def team_dto_from_grid(series_state_team):
    return {
        "bans": {},
        "objectives": process_team_objectives(series_state_team),
        "team_id": 100 if series_state_team.side == "blue" else 200,
        "win": series_state_team.won,
        "fk_team_id": series_state_team.id
    }