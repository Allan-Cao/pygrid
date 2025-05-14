# pythongrid
Simple Python based client for the GRID esports API with a collection of data pipeline functions to support processing of game data.

## Features / TODO
- [x] Rate limited access to GRID GraphQL endpoints
- [x] Simple client class to access commonly used queries.
- [x] Automatic pagination for queries that require multiple API calls
- [ ] Release my scripts that parse returned data files ideally in a database agnositic format. As I don't expect this library to become that popular, my main focus will be on compatability with my own [ATG](https://github.com/Allan-Cao/ATG) database format.
- [ ] Complete unit testing coverage of all parsing functions.

## Example Usage

Client API key setup

```python
import os
from pythongrid.client import GridClient

client = GridClient(os.environ["GRID_API_KEY"])
```

Lookup series information with filtering
```python
from pythongrid import OrderDirection, SeriesType
gte = "2025-01-01T00:00:00.000Z"
tournaments = ["825437", "825439", "825438", "825440", "825441"]
available_series = client.get_all_matches(
    order=OrderDirection.DESC,
    title_ids = [3], # LoL
    gte = gte, # Earliest series time
    tournaments = tournaments,
)
```

## Generating API code with Ariadne Codegen
Ariadne Codegen lets us translate raw GraphQL queries into a Python library as well as bringing GraphQL's type safety to Python

You'll need to set your GRID API key to be able to access the central data GraphQL API
```bash
export GRID_API_KEY=YOUR_KEY_HERE
```

To regenerate the GraphQL Client code use the following commands
```bash
ariadne-codegen --config central-data.toml
ariadne-codegen --config series-state.toml
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
