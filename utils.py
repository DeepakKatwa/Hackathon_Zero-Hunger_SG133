def get_priority(expiry):
    if expiry <= 3:
        return "High"
    elif expiry <= 6:
        return "Medium"
    else:
        return "Low"