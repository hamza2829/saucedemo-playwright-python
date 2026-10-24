# SauceDemo Playwright tests

Python UI tests for the public SauceDemo shop. This repository tests login, product sorting, cart changes and checkout. It uses page objects, pytest fixtures, parametrization and Playwright assertions. Verification and failure-drill evidence will be added after actual runs.

## Local setup on Windows

Python 3.12 and internet access are required. No Docker is used.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium firefox
.\.venv\Scripts\python.exe -m pytest --browser chromium --browser firefox --html=reports/all.html --self-contained-html
```

Open `reports/all.html`. Tests use the demo site's published users and password. They do not need personal credentials.

## Structure and marker strategy

- `pages/login.py`: login fields and submission.
- `pages/inventory.py`: products, sorting, add/remove and cart navigation.
- `pages/checkout.py`: cart, customer form, order summary and confirmation.
- `tests/`: feature groups, with no selectors in tests.
- `conftest.py`: fresh browser context per test, shared page fixtures, failure PNGs and trace ZIPs. Failure screenshots are also embedded in HTML reports.

| Feature | Cases | Smoke | Regression |
| --- | ---: | ---: | ---: |
| Login | 6 | 1 | 5 |
| Inventory | 8 | 1 | 7 |
| Checkout | 6 | 1 | 5 |
| Total per browser | 20 | 3 | 17 |

Markers are disjoint. Smoke covers valid login, add to cart and full checkout. Regression covers invalid and empty inputs, all four sort orders, removal, badge counts, cancellation and independent subtotal/tax/total expectations. Parametrized cases count as separate tests.

```powershell
.\.venv\Scripts\python.exe -m pytest -m smoke --browser chromium
.\.venv\Scripts\python.exe -m pytest -m regression --browser chromium
```

All UI checks use auto-retrying `expect` assertions. Actions use Playwright's auto waiting. There are no fixed sleeps or automatic retries hiding failed tests.

## CI and reports

GitHub Actions installs Python dependencies and browser system dependencies, then runs smoke followed by regression in each Chromium/Firefox matrix job. If smoke fails, that browser's regression step is skipped. The two browser jobs can run concurrently; tests within each job run sequentially. No pytest-xdist is configured.

Reports, JUnit XML, console logs and any failure screenshots/traces are uploaded even when a test fails. Artifacts are kept for 30 days. Download and unzip the artifact, then open `reports/regression.html`. Open a trace locally with:

```powershell
.\.venv\Scripts\python.exe -m playwright show-trace path\to\trace.zip
```

## Optional AI failure summary

`ai_failure_summary.py` reads a pytest log and calls the OpenAI Responses API only when both `OPENAI_API_KEY` and `OPENAI_MODEL` are set. It is an optional helper, not part of the pass/fail decision and not enabled in CI. It skips with exit code 0 when configuration is absent. No keys belong in this repository.

Review the log before sending it to an API. Basic key and bearer-token redaction is included, but is not comprehensive. The helper sends at most the last 18,000 characters and requests `store: false`.

```powershell
# Set OPENAI_API_KEY securely in your local environment, never in a committed file.
$env:OPENAI_MODEL = "your-available-model-id"
.\.venv\Scripts\python.exe ai_failure_summary.py reports\regression.log
```

## Limits

Demo site only. No real payment, production system, API coverage, accessibility audit or visual regression testing. This suite requires the public site's availability and assumes its published catalog prices. Only Chromium and Firefox are in scope. Screenshots are debugging evidence, not pixel comparison tests. Browser crashes or launch failures can prevent screenshots; traces cover browser actions and DOM snapshots, while assertion details are in the pytest report.

## References

- [Playwright Python assertions](https://playwright.dev/python/docs/test-assertions)
- [Playwright trace viewer](https://playwright.dev/python/docs/trace-viewer)
- [pytest-html reports](https://pytest-html.readthedocs.io/en/stable/user_guide.html)
- [OpenAI text generation](https://developers.openai.com/api/docs/guides/text)
