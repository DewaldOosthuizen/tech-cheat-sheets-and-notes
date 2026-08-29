# Tech Cheat Sheets And Notes

[![Lint](https://github.com/DewaldOosthuizen/tech-cheat-sheets-and-notes/actions/workflows/lint.yml/badge.svg?branch=main&event=push)](https://github.com/DewaldOosthuizen/tech-cheat-sheets-and-notes/actions/workflows/lint.yml)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/paypalme/DewaldOosthuizen1)

Quick-reference study notes for technology certifications and architecture decisions.
Each sheet answers *which service, which pattern, and why* — not how to click through a portal.
Content is comparison-oriented: tables, decision flowcharts, and Mermaid diagrams side-by-side.

---

## Cloud Service Providers

--8<-- "azure/index.md"

--8<-- "aws/index.md"

--8<-- "google/index.md"

---

## Programming

--8<-- "programming/java/index.md"

---

## How to Use These Sheets

The cheat sheets are not meant to be read cover-to-cover. Jump to the section relevant to what
you are studying. Each section contains:

- A comparison table of services in that domain
- Exam-tip callouts that highlight common decision points in exam questions
- One or more Mermaid decision flowcharts for branching "which service?" scenarios
- Deprecation notices where a service has been retired or superseded

The live site renders all diagrams inline. To browse locally, run `make docs-serve`.

---

## Contributing

See [CONTRIBUTING.md](https://github.com/DewaldOosthuizen/tech-cheat-sheets-and-notes/blob/main/CONTRIBUTING.md)
for the full contributor workflow.

## License

This project is licensed under the [`GPL-3.0`](https://github.com/DewaldOosthuizen/tech-cheat-sheets-and-notes/blob/main/LICENSE).
