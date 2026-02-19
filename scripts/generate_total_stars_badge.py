import os
import math
import requests
from pathlib import Path

USERNAME = os.environ.get("GH_USER", "Danilosouzax")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT_PATH = os.environ.get("OUT_PATH", "dist/badges/total-stars.svg")

def fetch_all_repos(username: str, token: str):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    repos = []
    page = 1
    per_page = 100

    while True:
        url = f"https://api.github.com/users/{username}/repos"
        r = requests.get(url, headers=headers, params={"per_page": per_page, "page": page, "type": "owner"})
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < per_page:
            break
        page += 1

    return repos

def human(n: int) -> str:
    if n < 1000:
        return str(n)
    if n < 1_000_000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    return f"{n/1_000_000:.1f}M".replace(".0M", "M")

def make_svg(label: str, value: str):
    # estilo “for-the-badge” simples (sem depender de shields)
    label_bg = "#0b1020"
    value_bg = "#f59e0b"
    text = "#ffffff"
    label = label.upper()

    # largura aproximada por caractere (monospace-ish)
    label_w = max(88, 12 * len(label) + 28)
    value_w = max(70, 12 * len(value) + 28)
    w = label_w + value_w
    h = 28

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" role="img" aria-label="{label}: {value}">
  <title>{label}: {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#fff" stop-opacity=".08"/>
    <stop offset="1" stop-color="#000" stop-opacity=".12"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{w}" height="{h}" rx="6" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_w}" height="{h}" fill="{label_bg}"/>
    <rect x="{label_w}" width="{value_w}" height="{h}" fill="{value_bg}"/>
    <rect width="{w}" height="{h}" fill="url(#s)"/>
  </g>
  <g fill="{text}" text-anchor="middle"
     font-family="Verdana, Geneva, DejaVu Sans, sans-serif"
     font-size="12" font-weight="700">
    <text x="{label_w/2}" y="19">{label}</text>
    <text x="{label_w + value_w/2}" y="19">{value}</text>
  </g>
</svg>'''
    return svg

def main():
    repos = fetch_all_repos(USERNAME, TOKEN)
    total = 0
    for repo in repos:
        # soma stargazers_count de cada repo
        total += int(repo.get("stargazers_count", 0))

    value = human(total)
    svg = make_svg("Stars (total)", value)

    out = Path(OUT_PATH)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")

    print(f"Total stars: {total} -> wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
