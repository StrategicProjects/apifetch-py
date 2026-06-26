"""Use case: the Big Data PE API.

`apifetch` was extracted from the BigDataPE package, which wraps the Big Data PE
platform — a public-data REST API run by the Government of the State of
Pernambuco, Brazil. This is the canonical worked example of configuring the
package for a real API.

What is specific about Big Data PE:

- Authentication sends the token *verbatim* in the ``Authorization`` header
  (no ``Bearer`` prefix)            -> ``AuthRaw()``
- Pagination sends ``limit``/``offset`` as HTTP *headers*, not query params
                                      -> ``PaginateOffset(where="header")``
- Responses carry a status column ``"Mensagem"`` we drop  -> ``drop_cols``
- The API is reachable only from the PE Conectado network or VPN -> ``connect_hint``
"""

import apifetch as af

bigdatape = af.Api(
    endpoint="https://www.bigdata.pe.gov.br/api/buscar",
    service="BigDataPE",
    auth=af.AuthRaw(),
    pagination=af.PaginateOffset(where="header"),
    drop_cols=("Mensagem",),
    connect_hint="Ensure you are on the PE Conectado network or VPN.",
)

if __name__ == "__main__":
    # Store your token (kept only in this process's environment).
    af.store_token("dengue", "your-token-here", service="BigDataPE")

    # A single page of 50 records.
    dengue = af.fetch(bigdatape, "dengue", limit=50)
    print(f"got {len(dengue)} records")

    # Everything, in chunks, with a progress message per chunk.
    dengue_all = af.fetch_all(bigdatape, "dengue", chunk_size=50_000, verbosity=1)
    print(f"got {len(dengue_all)} records total")

    # Optional: a DataFrame.
    # import pandas as pd
    # df = pd.DataFrame(dengue_all)
