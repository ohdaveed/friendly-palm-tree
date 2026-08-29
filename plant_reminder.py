#!/usr/bin/env python3
"""Plant Watering Reminder - A simple CLI app to remind you to water your plants."""

import argparse
import json
import os
from datetime import date, timedelta

DATA_FILE = os.path.join(os.path.dirname(__file__), "plants.json")


def load_plants():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}


def save_plants(plants):
    with open(DATA_FILE, "w") as f:
        json.dump(plants, f, indent=2)


def add_plant(name, interval_days):
    plants = load_plants()
    plants[name] = {
        "interval_days": interval_days,
        "last_watered": date.today().isoformat(),
    }
    save_plants(plants)
    print(f"Added plant '{name}' with a watering interval of every {interval_days} day(s).")


def list_plants():
    plants = load_plants()
    if not plants:
        print("No plants added yet. Use 'add' to add your first plant.")
        return
    today = date.today()
    print(f"{'Plant':<20} {'Interval':>10} {'Last Watered':>15} {'Next Watering':>15} {'Status':>12}")
    print("-" * 75)
    for name, info in plants.items():
        last = date.fromisoformat(info["last_watered"])
        interval = info["interval_days"]
        next_water = last + timedelta(days=interval)
        days_left = (next_water - today).days
        if days_left < 0:
            status = f"OVERDUE {abs(days_left)}d"
        elif days_left == 0:
            status = "TODAY!"
        else:
            status = f"in {days_left}d"
        print(f"{name:<20} {interval:>10} {last.isoformat():>15} {next_water.isoformat():>15} {status:>12}")


def water_plant(name):
    plants = load_plants()
    if name not in plants:
        print(f"Plant '{name}' not found. Use 'list' to see your plants.")
        return
    plants[name]["last_watered"] = date.today().isoformat()
    save_plants(plants)
    today_str = plants[name]["last_watered"]
    print(f"Marked '{name}' as watered today ({today_str}).")


def check_reminders():
    plants = load_plants()
    if not plants:
        print("No plants to check.")
        return
    today = date.today()
    needs_water = []
    for name, info in plants.items():
        last = date.fromisoformat(info["last_watered"])
        next_water = last + timedelta(days=info["interval_days"])
        if next_water <= today:
            needs_water.append((name, (today - next_water).days))

    if needs_water:
        print("🌱 Watering Reminders:")
        for name, overdue in needs_water:
            if overdue == 0:
                print(f"  • {name} — needs water TODAY!")
            else:
                print(f"  • {name} — overdue by {overdue} day(s)!")
    else:
        print("✅ All plants are up to date — nothing to water today!")


def remove_plant(name):
    plants = load_plants()
    if name not in plants:
        print(f"Plant '{name}' not found.")
        return
    del plants[name]
    save_plants(plants)
    print(f"Removed plant '{name}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Plant Watering Reminder — keep your plants happy!"
    )
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Add a new plant")
    add_parser.add_argument("name", help="Plant name")
    add_parser.add_argument(
        "interval", type=int, help="Watering interval in days (e.g. 3 for every 3 days)"
    )

    subparsers.add_parser("list", help="List all plants and their watering schedule")
    subparsers.add_parser("remind", help="Show plants that need watering today")

    water_parser = subparsers.add_parser("water", help="Mark a plant as watered today")
    water_parser.add_argument("name", help="Plant name")

    remove_parser = subparsers.add_parser("remove", help="Remove a plant")
    remove_parser.add_argument("name", help="Plant name")

    args = parser.parse_args()

    if args.command == "add":
        add_plant(args.name, args.interval)
    elif args.command == "list":
        list_plants()
    elif args.command == "remind":
        check_reminders()
    elif args.command == "water":
        water_plant(args.name)
    elif args.command == "remove":
        remove_plant(args.name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
