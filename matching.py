def match_food(surplus, demand):
    matches = []

    # Initialize tracking
    for s in surplus:
        s["original"] = s.get("original", s["qty"])
        s["matched"] = 0

    for d in demand:
        d["original"] = d.get("original", d["qty"])
        d["matched"] = 0

    # Matching logic
    for s in surplus:
        for d in demand:
            if s["qty"] > 0 and d["qty"] > 0:
                m = min(s["qty"], d["qty"])

                matches.append({
                    "from": s["name"],
                    "to": d["name"],
                    "qty": m
                })

                s["qty"] -= m
                d["qty"] -= m

                s["matched"] += m
                d["matched"] += m

    return matches