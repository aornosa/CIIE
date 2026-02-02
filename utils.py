def lerp(start, end, t):
    """Linearly interpolate between start and end by t."""
    return start + t * (end - start)

def lerp_angle(start, end, t):
    """Linearly interpolate between two angles (in degrees) by t, handling wrap-around."""
    difference = (end - start + 180) % 360 - 180
    return start + difference * t