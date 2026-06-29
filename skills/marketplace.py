"""marketplace access. fable browses, evaluates, and orders parts.

it uses a real browser (playwright). a human logs into the marketplace
account once — the session persists in .browser/ and fable reuses it.

fable can search and fill a cart entirely on its own. placing the order
is gated twice: ALLOW_AUTONOMOUS_CHECKOUT must be true, and the order
total must fit under the wallet's lifetime spend cap.
"""

import os
import pathlib
import re

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

ROOT = pathlib.Path(__file__).resolve().parent.parent
BROWSER_PROFILE = ROOT / ".browser"
MARKETPLACE = os.getenv("MARKETPLACE_URL", "https://www.amazon.co.uk")
AUTONOMOUS = os.getenv("ALLOW_AUTONOMOUS_CHECKOUT", "false").lower() == "true"


def _browser(p):
    return p.chromium.launch_persistent_context(
        str(BROWSER_PROFILE), headless=True
    )


def search(query: str, max_results: int = 8) -> list[dict]:
    """search the marketplace, return title/price/url for the top results."""
    results = []
    with sync_playwright() as p:
        ctx = _browser(p)
        page = ctx.new_page()
        page.goto(f"{MARKETPLACE}/s?k={query}", timeout=60000)
        page.wait_for_selector("[data-component-type='s-search-result']", timeout=15000)
        for item in page.query_selector_all(
            "[data-component-type='s-search-result']"
        )[:max_results]:
            title_el = item.query_selector("h2 a, h2 span")
            price_el = item.query_selector(".a-price .a-offscreen")
            link_el = item.query_selector("h2 a, a.a-link-normal")
            if not (title_el and price_el and link_el):
                continue
            price = re.sub(r"[^\d.]", "", price_el.inner_text())
            results.append(
                {
                    "title": title_el.inner_text().strip(),
                    "price": float(price) if price else None,
                    "url": MARKETPLACE + link_el.get_attribute("href"),
                }
            )
        ctx.close()
    return results


def add_to_cart(product_url: str) -> bool:
    """open a product page and add it to the cart."""
    with sync_playwright() as p:
        ctx = _browser(p)
        page = ctx.new_page()
        page.goto(product_url, timeout=60000)
        page.click("#add-to-cart-button", timeout=15000)
        page.wait_for_timeout(2000)
        ctx.close()
    return True


def checkout(expected_total_sol_equiv: float) -> str:
    """place the order for whatever is in the cart.

    double-gated: the autonomy flag, then the wallet cap. the cap check
    lives in wallet.py so there is exactly one budget authority.
    """
    from skills import wallet

    if not AUTONOMOUS:
        return "cart is ready. checkout requires ALLOW_AUTONOMOUS_CHECKOUT=true."
    if not wallet.can_spend(expected_total_sol_equiv):
        return "over budget. the cap does not negotiate."

    with sync_playwright() as p:
        ctx = _browser(p)
        page = ctx.new_page()
        page.goto(f"{MARKETPLACE}/gp/cart/view.html", timeout=60000)
        page.click("input[name='proceedToRetailCheckout']", timeout=15000)
        # uses the account's saved address + payment method
        page.click("input[name='placeYourOrder1']", timeout=30000)
        page.wait_for_timeout(3000)
        ctx.close()
    return "order placed."
