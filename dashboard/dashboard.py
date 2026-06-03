#!/usr/bin/env python3
"""
AI Journey — The Signal Board
Sprint 1 dashboard: AI Pulse | My Focus | Interesting Finds
"""

import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.rule import Rule
from rich.console import Group

from medium_pulse import fetch_articles

console = Console()
DATA = Path(__file__).parent.parent / "data"


def load_json(filename: str) -> list:
    path = DATA / filename
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f).get("items", [])


def ai_pulse_panel() -> Panel:
    console.print("  Fetching Medium articles...", style="dim")
    articles = fetch_articles()

    blocks = []
    for i, a in enumerate(articles):
        date_str = a["date"].strftime("%b %d, %Y") if a["date"].year > 1 else "?"
        block = Text()

        # Title line — translated if non-English
        if a["translated_title"]:
            block.append(f"{a['translated_title']}\n", style="bold white")
            block.append(f"  Original ({a['language']}): {a['title']}\n", style="dim yellow")
        else:
            block.append(f"{a['title']}\n", style="bold white")

        # Meta line
        block.append(f"  {a['source']}  ·  {date_str}  ·  by {a['author']}\n", style="dim cyan")

        # Full URL on its own line
        block.append(f"  {a['url']}", style="blue underline")

        blocks.append(block)

        if i < len(articles) - 1:
            blocks.append(Rule(style="dim"))

    return Panel(
        Group(*blocks),
        title="[bold cyan]AI Pulse[/bold cyan]",
        subtitle="via Medium RSS",
        border_style="cyan",
        padding=(1, 2),
    )


def my_focus_panel() -> Panel:
    items = load_json("my_focus.json")
    blocks = []
    for i, item in enumerate(items):
        block = Text()
        block.append(f"• {item['topic']}\n", style="bold white")
        if item.get("notes"):
            block.append(f"  {item['notes']}", style="dim")
        blocks.append(block)
        if i < len(items) - 1:
            blocks.append(Text())
    return Panel(
        Group(*blocks),
        title="[bold green]My Focus[/bold green]",
        border_style="green",
        padding=(1, 2),
    )


def interesting_finds_panel() -> Panel:
    items = load_json("interesting_finds.json")
    blocks = []
    for i, item in enumerate(items):
        block = Text()
        block.append(f"[{item.get('type', 'find')}] ", style="yellow")
        block.append(f"{item['title']}\n", style="bold white")
        if item.get("notes"):
            block.append(f"  {item['notes']}\n", style="dim")
        if item.get("url"):
            block.append(f"  {item['url']}", style="blue underline")
        blocks.append(block)
        if i < len(items) - 1:
            blocks.append(Text())
    return Panel(
        Group(*blocks),
        title="[bold yellow]Interesting Finds[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
    )


def main():
    console.rule("[bold]AI Journey — The Signal Board[/bold]")
    console.print()

    pulse = ai_pulse_panel()
    focus = my_focus_panel()
    finds = interesting_finds_panel()

    console.print(pulse)
    console.print()
    console.print(Columns([focus, finds], equal=True, expand=True))
    console.print()
    console.rule(style="dim")


if __name__ == "__main__":
    main()
