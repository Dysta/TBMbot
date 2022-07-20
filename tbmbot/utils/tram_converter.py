from typing import Dict

_tram: Dict[str, str] = {"59": "A", "60": "B", "61": "C", "62": "D"}


def get_tram_schedule_id(id: str) -> str:
    """Return the tram id if the line id is a tram line

    Parameters
    ----------
    id : str
        The line id to convert

    Returns
    -------
    str
        The line id converted if the given line is a tram line
    """
    return _tram.get(id, id)
