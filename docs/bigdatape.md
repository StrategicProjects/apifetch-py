# Use case: the Big Data PE API

`apifetch` was extracted from the
[BigDataPE](https://github.com/StrategicProjects/BigDataPE) package, which wraps
the **Big Data PE** platform — a public-data REST API run by the Government of
the State of Pernambuco, Brazil. This page is the canonical worked example of
configuring the package for a real API.

## What is specific about Big Data PE

| Convention | Strategy |
|---|---|
| Token sent *verbatim* in the `Authorization` header (no `Bearer`) | `AuthRaw()` |
| `limit`/`offset` sent as **HTTP headers**, not query params | `PaginateOffset(where="header")` |
| Responses carry a status column `"Mensagem"` to drop | `drop_cols=("Mensagem",)` |
| Reachable only from the PE Conectado network / VPN | `connect_hint=...` |

## Defining the profile

```python
import apifetch as af

bigdatape = af.Api(
    endpoint="https://www.bigdata.pe.gov.br/api/buscar",
    service="BigDataPE",
    auth=af.AuthRaw(),
    pagination=af.PaginateOffset(where="header"),
    drop_cols=("Mensagem",),
    connect_hint="Ensure you are on the PE Conectado network or VPN.",
)
```

## Storing a token and fetching

```python
af.store_token("dengue", "your-token-here", service="BigDataPE")

# A single page of 50 records
dengue = af.fetch(bigdatape, "dengue", limit=50)

# Everything, in chunks, with a progress message per chunk
dengue_all = af.fetch_all(bigdatape, "dengue", chunk_size=50_000, verbosity=1)
```

!!! note "On language"
    Function and parameter names are English, but the API's response keys and
    some values are Portuguese (e.g. `nu_notificacao`, `"BOA VIAGEM"`). That is
    intentional — they come straight from the upstream service.
