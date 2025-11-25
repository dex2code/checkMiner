from loguru import logger


@logger.catch
def convert_hashrate(s: str) -> int:
    """
    Converts hashrate from str 600G to normal 600_000_000_000 int | 
    Thanks ckpool for this :)
    """
    result = 0

    multipliers = {
        'K': 1_000,
        'M': 1_000_000,
        'G': 1_000_000_000,
        'T': 1_000_000_000_000,
        'P': 1_000_000_000_000_000
    }

    if not isinstance(s, str):
        raise ValueError(f"Expected argument 's' is not a string!")

    s = s.strip()
    if not s:
        raise ValueError(f"Expected argument 's' is empty!")
    
    suffix_index = -1
    for i, char in enumerate(s):
        if char in multipliers:
            suffix_index = i
            break
    
    if suffix_index == -1:
        try:
            return int(s)
        except ValueError as e:
            raise ValueError(f"Wrong format of 's' is given! {s=} - {e}")
    
    number_part = s[:suffix_index]
    multiplier = s[suffix_index]

    try:
        number = float(number_part)
        result = int(number * multipliers[multiplier])
    except ValueError as e:
        raise ValueError(f"Wrong number in 's' is given {number_part=} - {e}")

    return result


if __name__ == "__main__":
    pass