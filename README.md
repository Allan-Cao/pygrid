# GRID-ingest
Simple Python GRID API and associated scripts.

## TODO
- Add my scripts that parses returned data files ideally in a database agnositic format. As I don't expect this library to become that popular, my main focus will be on compatability with my own [ATG](https://github.com/Allan-Cao/ATG) database format.
- Release unit tested parsing functions.
- Properly rate limit usage (sorry GRID that was me doing an accidental query burst the other day).

## Usage

Example setup

```python
from GRID.central_data.enums import SeriesType, OrderDirection
from GRID.central_data.client import Client as CentralDataClient
from GRID.series_state.client import Client as SeriesStateClient

central_data_client = CentralDataClient("https://api.grid.gg/central-data/graphql", {"x-api-key": GRID_API_KEY})
series_state_client = SeriesStateClient("https://api.grid.gg/live-data-feed/series-state/graphql", {"x-api-key": GRID_API_KEY})
```

Example usage to get all tournaments (naive rate limit)
```python
def get_available_tournaments(central_data_client, rate_limit: int = 3) -> list:
    tournaments = []
    after = None
    has_next_page = True

    while has_next_page:
        time.sleep(rate_limit)
        temp_tournaments = central_data_client.get_available_tournaments(after, 50)
        tournaments.extend(temp_tournaments.tournaments.edges)
        has_next_page = temp_tournaments.tournaments.page_info.has_next_page
        after = temp_tournaments.tournaments.page_info.end_cursor
    return tournaments
```

## Generating code with Ariadne Codegen
Ariadne Codegen lets us translate raw GraphQL queries into a usable Python library with support for type checking.

First, you'll need to set the environment variable
```bash
export GRID_API_KEY=YOUR_KEY_HERE
```

```bash
ariadne-codegen --config central-data.toml
ariadne-codegen --config series-state.toml
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
