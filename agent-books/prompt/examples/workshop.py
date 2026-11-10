"""Pure, offline teaching example; faulty mode intentionally violates R01-v1."""
from __future__ import annotations

import argparse
import json


def valid_state(capacity, confirmed, waiting, person, action):
    if type(capacity) is not int or capacity < 0:
        return False
    if not isinstance(confirmed, list) or not isinstance(waiting, list):
        return False
    people = confirmed + waiting + [person]
    if any(not isinstance(item, str) or not item.strip() for item in people):
        return False
    registered = confirmed + waiting
    return (len(set(registered)) == len(registered)
            and len(confirmed) <= capacity
            and (not waiting or len(confirmed) == capacity)
            and action in ("register", "cancel"))


def transition(capacity, confirmed, waiting, person, action, *, faulty=False):
    """Return a new state. No network, clock, identity lookup or persistence."""
    if not valid_state(capacity, confirmed, waiting, person, action):
        return {"status": "invalid", "confirmed": confirmed, "waiting": waiting}
    confirmed, waiting = confirmed.copy(), waiting.copy()
    if action == "register":
        duplicate = person in confirmed or (not faulty and person in waiting)
        if duplicate:
            status = "duplicate"
        elif len(confirmed) < capacity or (faulty and len(confirmed) == capacity):
            confirmed.append(person)
            status = "confirmed"
        else:
            waiting.append(person)
            status = "waiting"
    elif person in confirmed:
        confirmed.remove(person)
        if waiting and not faulty:
            confirmed.append(waiting.pop(0))
        status = "cancelled"
    elif person in waiting:
        waiting.remove(person)
        status = "cancelled"
    else:
        status = "not_found"
    return {"status": status, "confirmed": confirmed, "waiting": waiting}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", help="Path to a JSON request")
    parser.add_argument("--mode", choices=("faulty", "reference"), default="faulty")
    args = parser.parse_args()
    with open(args.request, encoding="utf-8-sig") as stream:
        request = json.load(stream)
    result = transition(**request, faulty=args.mode == "faulty")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
