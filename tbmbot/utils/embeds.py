from datetime import datetime
from urllib.parse import quote

from markdownify import markdownify
from disnake import Embed, Colour

from tbmbot.models import LineInformation, Alerts

from ..utils import cleaner

_BASE_FREQ_PATH: str = (
    "https://www.infotbm.com/sites/default/files/frequentation/%s.png"
)

VOID_TOKEN = "\u200B"


def line_info_embed(line_data: LineInformation) -> Embed:
    line_id: str = line_data.external_code
    e: Embed = Embed(
        title=f"{line_data.name}",
        description="",
        colour=Colour(int(line_data.color, base=16)),
    )
    for l in line_data.line_schedules:
        date_begin = datetime.strptime(l.begin, "%Y-%m-%dT%H:%M:%S%z")
        date_end = datetime.strptime(l.end, "%Y-%m-%dT%H:%M:%S%z")
        e.add_field(
            name=f"Horaire : {date_begin.strftime('%d/%m/%Y')} — {date_end.strftime('%d/%m/%Y')}",
            value=f"{l.navigation_amplitude} — {l.frequency}",
            inline=False,
        )
    e.set_image(url=quote(line_data.line_maps[0].thermometer_image).replace("%3A", ":"))
    e.set_thumbnail(url=_BASE_FREQ_PATH % line_id)
    return e


def line_perturbation_embed(alerts_data: Alerts) -> Embed:
    e: Embed = Embed(title="Perturbations", description="", colour=0xDB3C30)
    for p in alerts_data.__root__[0].impacts:
        e.add_field(
            name=f"⚠ | {'🟥' if not p.alert.working_network else '🟩'} {p.alert.cause_name} | {p.alert.title}",
            value=markdownify(cleaner.clean_description(p.alert.description)),
            inline=False,
        )

    return e
