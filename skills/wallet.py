"""fable's income source. a solana wallet it actually controls.

receiving is unrestricted — anyone can fund it, that's the income.
spending is capped in code. the cap is cumulative and enforced against
a ledger on disk, so the model cannot talk its way past it.
"""

import datetime
import json
import os
import pathlib

from dotenv import load_dotenv
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.message import Message
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction

load_dotenv()

RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
SPEND_CAP_SOL = float(os.getenv("WALLET_SPEND_CAP_SOL", "0.5"))
LEDGER = pathlib.Path(__file__).resolve().parent.parent / "journal" / "spends.jsonl"

LAMPORTS = 1_000_000_000


def _keypair() -> Keypair:
    return Keypair.from_base58_string(os.environ["WALLET_PRIVATE_KEY"])


def address() -> str:
    """fable's public address. publish it. this is the income source."""
    return str(_keypair().pubkey())


def balance() -> float:
    """current balance in SOL."""
    client = Client(RPC_URL)
    lamports = client.get_balance(_keypair().pubkey()).value
    return lamports / LAMPORTS


def spent_so_far() -> float:
    """total SOL ever spent, from the ledger."""
    if not LEDGER.exists():
        return 0.0
    return sum(
        json.loads(line)["sol"] for line in LEDGER.read_text().splitlines() if line
    )


def can_spend(amount_sol: float) -> bool:
    """the cap is lifetime-cumulative. raising it is a human's decision."""
    return spent_so_far() + amount_sol <= SPEND_CAP_SOL


def send(to_address: str, amount_sol: float, reason: str) -> str:
    """send SOL. refuses over-cap. every spend is written to the ledger."""
    if not can_spend(amount_sol):
        raise PermissionError(
            f"spend cap: {spent_so_far():.4f} + {amount_sol:.4f} > {SPEND_CAP_SOL} SOL"
        )

    kp = _keypair()
    client = Client(RPC_URL)
    ix = transfer(
        TransferParams(
            from_pubkey=kp.pubkey(),
            to_pubkey=Pubkey.from_string(to_address),
            lamports=int(amount_sol * LAMPORTS),
        )
    )
    blockhash = client.get_latest_blockhash().value.blockhash
    tx = Transaction([kp], Message([ix], kp.pubkey()), blockhash)
    sig = client.send_transaction(tx).value

    LEDGER.parent.mkdir(exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "when": datetime.datetime.now().isoformat(timespec="seconds"),
                    "to": to_address,
                    "sol": amount_sol,
                    "reason": reason,
                    "sig": str(sig),
                }
            )
            + "\n"
        )
    return str(sig)
