# boundaries

fable acts in the real world — it can hold money, spend it, and place orders.
that is the point, and it is also why the limits below are enforced in code
rather than left to the model or to trust.

- **it only ever touches accounts its operator owns and funds.** the wallet,
  the marketplace login, and the x account all belong to the human running
  it. nothing here reaches anyone else's account, and nothing is built to.
- **spending is capped in code.** the cap is lifetime-cumulative and checked
  against a ledger on disk before any transfer. the model cannot raise it and
  cannot talk past it.
- **autonomous checkout is off by default.** fable can research and fill a
  cart on its own; placing an order is a deliberate decision by the operator.
- **no credentials live here.** keys and logins stay out of the repository,
  and the history has been kept clean of them.

this repository is a record, not a distribution — see `NOTICE`. there is
nothing here to install.
