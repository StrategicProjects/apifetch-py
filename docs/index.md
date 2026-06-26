<p align="center">
  <img src="assets/logo.svg" width="200" alt="apifetch">
</p>

# apifetch

A small, dependency-light toolkit for talking to **token-authenticated REST
APIs**. It handles three recurring chores:

1. **Token management** — store/get/remove/list tokens in process environment
   variables (never written to disk), namespaced per service.
2. **Request building** — pluggable **authentication** and **pagination**
   strategies, bundled into a reusable [`Api`](reference.md) profile.
3. **Data retrieval** — fetch one page, or fetch everything in chunks.

This is the Python sibling of the R package
[apifetch](https://github.com/StrategicProjects/apifetch).

## Installation

```bash
pip install apifetch
```

## Quick start

```python
import apifetch as af

api = af.Api(
    endpoint="https://api.example.com/v1/search",
    service="Example",
    auth=af.AuthBearer(),                 # "Authorization: Bearer <token>"
    pagination=af.PaginateOffset(where="query"),
)

af.store_token("reports", "my-secret-token", service="Example")

one_page = af.fetch(api, "reports", limit=50)
everything = af.fetch_all(api, "reports", chunk_size=1000)
```

### Strategies

**Authentication:** `AuthBearer`, `AuthRaw`, `AuthHeader`, `AuthQuery`.

**Pagination:** `PaginateOffset(where="header" | "query")`, `PaginateNone`.

See the [BigDataPE use case](bigdatape.md) for a real-world configuration, or the
full [API reference](reference.md).
