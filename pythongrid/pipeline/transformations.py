import httpx
import orjson

from .constants import (
    SHARED_LIVE_STATS_EVENT_KEYS,
    DRAFT_TURNS_BLUE,
    DRAFT_TURNS_RED,
    NAME_ID_MAP,
)
from typing import List


def process_live_stats(live_stats_input: str | httpx.Response):
    """Data transformation from riot live stats file or httpx stream to riot live stats jsonl

    Args:
        live_stats_input (str | httpx.stream): Input file or httpx Reponse object to download series

    Returns:
        game_participant_info (dict): game_info event
        game_end_event (dict): game_end event
        final_stats_update (dict): The final stats_update event
        final_champ_select (dict): The final champ_select event which contains the completed draft
        saved_events (list): All events except for champ_select events
    """
    saved_events = []
    game_participant_info = None
    game_end_event = None
    final_stats_update = None
    final_champ_select = None

    # Not sure of a cleaner way to write this that is also simple.
    if isinstance(live_stats_input, str):
        # orjsonl should be used when we need to support compression.
        with open(live_stats_input, "rb") as input_stream:
            for line in input_stream:
                if line:
                    event = orjson.loads(line)
                    schema = event["rfc461Schema"]
                    if schema == "game_info":
                        game_participant_info = event
                        event["gameTime"] = (
                            -1
                        )  # The game_info event is missing a gameTime which causes future processing to fail.
                    if schema == "game_end":
                        game_end_event = event
                    if schema == "stats_update":
                        final_stats_update = event
                    # Only champ select events need to be handeled differently
                    if schema == "champ_select":
                        final_champ_select = event
                    else:
                        saved_events.append(event)
    else:
        with live_stats_input as input_stream:
            for line in input_stream.iter_lines():
                if line:
                    event = orjson.loads(line)
                    schema = event["rfc461Schema"]
                    if schema == "game_info":
                        game_participant_info = event
                        event["gameTime"] = (
                            -1
                        )  # The game_info event is missing a gameTime which causes future processing to fail.
                    if schema == "game_end":
                        game_end_event = event
                    if schema == "stats_update":
                        final_stats_update = event
                    # Only champ select events need to be handeled differently
                    if schema == "champ_select":
                        final_champ_select = event
                    else:
                        saved_events.append(event)
    return (
        game_participant_info,
        game_end_event,
        final_stats_update,
        final_champ_select,
        saved_events,
    )


def process_event(event: dict, game_id: str) -> dict:
    """
    Parse a single game event into a game event dictionary by removing shared keys.

    Args:
        event: Event data dictionary
        game_id: Game ID

    Returns:
        ATG Game event formatted dictionary
    """
    # Extract schema information
    schema = event["rfc461Schema"]
    sequence_index = event["sequenceIndex"]
    game_time = event["gameTime"]

    # Extract event-specific details
    event_details = {
        key: value
        for key, value in event.items()
        if key not in SHARED_LIVE_STATS_EVENT_KEYS
    }

    return {
        "game_id": game_id,
        "schema": schema,
        "sequence_index": sequence_index,
        "game_time": game_time,
        "additional_details": event_details,
    }


def process_pick_bans(
    blue_draft: List[dict],
    red_draft: List[dict],
    bans: List[dict],
    game_participant_info: dict,
    game_id: str,
) -> List[dict]:
    pick_bans = []

    P_MAP = {
        NAME_ID_MAP.get(participant["championName"].lower()): participant[
            "participantID"
        ]
        for participant in game_participant_info["participants"]
    }

    for i, (blue, red) in enumerate(zip(blue_draft, red_draft)):
        is_phase_one = i < 3

        pick_bans.append(
            {
                "game_id": game_id,
                "champion_id": blue,
                "participant_id": P_MAP[blue],
                "is_pick": True,
                "is_phase_one": is_phase_one,
                "is_blue": True,
                "pick_turn": DRAFT_TURNS_BLUE[i],
            }
        )
        pick_bans.append(
            {
                "game_id": game_id,
                "champion_id": red,
                "participant_id": P_MAP[red],
                "is_pick": True,
                "is_phase_one": is_phase_one,
                "is_blue": True,
                "pick_turn": DRAFT_TURNS_RED[i],
            }
        )

    for idx, ban in enumerate(bans):
        pick_bans.append(
            {
                "game_id": game_id,
                "champion_id": ban["championID"],
                "participant_id": None,
                "is_pick": False,
                "is_phase_one": idx < 6,
                "is_blue": ban["teamID"] == 100,
                "pick_turn": ban["pickTurn"],
            }
        )

    return pick_bans
