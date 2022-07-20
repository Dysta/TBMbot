from datetime import datetime
from typing import List
from urllib.parse import quote

from disnake import Colour, Embed
from markdownify import markdownify
from tbmbot.models import Alerts, LineInformation, Schedule

from ..utils import cleaner

_BASE_FREQ_PATH: str = (
    "https://www.infotbm.com/sites/default/files/frequentation/%s.png"
)

VOID_TOKEN = "\u200B"


def line_info_embed(line_data: LineInformation) -> List[Embed]:
    line_id: str = line_data.external_code
    e1: Embed = Embed(
        title=f"{line_data.name}",
        description="",
        colour=Colour(int(line_data.color, base=16)),
        url="https://www.infotbm.com/fr/horaires/recherche?line=%s" % line_id,
    )
    e1.add_field(
        name="Terminus :",
        value=f"{line_data.terminus[0].stop_points[0].full_label} ↔️ {line_data.terminus[1].stop_points[0].full_label}",
        inline=False,
    )
    for l in line_data.line_schedules:
        date_begin = datetime.strptime(l.begin, "%Y-%m-%dT%H:%M:%S%z")
        date_end = datetime.strptime(l.end, "%Y-%m-%dT%H:%M:%S%z")
        e1.add_field(
            name=f"Horaire : {date_begin.strftime('%d/%m/%Y')} — {date_end.strftime('%d/%m/%Y')}",
            value=f"{l.navigation_amplitude} — {l.frequency}",
            inline=False,
        )
    e1.set_image(
        url=quote(line_data.line_maps[0].thermometer_image).replace("%3A", ":")
    )
    e2: Embed = Embed(
        url="https://www.infotbm.com/fr/horaires/recherche?line=%s" % line_id,
    )
    e2.set_image(url=_BASE_FREQ_PATH % line_id)
    return [e1, e2]


def line_perturbation_embed(alerts_data: Alerts) -> Embed:
    e: Embed = Embed(title="Perturbations", description="", colour=0xDB3C30)
    for p in alerts_data.__root__[0].impacts:
        e.add_field(
            name=f"⚠ | {'🟥' if not p.alert.working_network else '🟩'} {p.alert.cause_name} | {p.alert.title}",
            value=markdownify(cleaner.clean_description(p.alert.description)),
            inline=False,
        )

    return e


def line_schedule_embed(title: str, schedules: List[Schedule]) -> Embed:
    e: Embed = Embed(title=title, description="", colour=0x039CD2)
    # count how many field we put to see if we must put a reset field
    placed_field: int = 0
    for i, schedule in enumerate(schedules, start=1):
        v = "\n".join([f"`{e.waittime_text}`" for e in schedule.__root__])
        e.add_field(
            name=f"__{schedule.__root__[0].line_name}__ ➡️ {schedule.__root__[0].destination_name}",
            value=v,
            inline=True,
        )
        placed_field += 1

        zz = schedules[i].__root__[0].line_name if i < len(schedules) else ""
        cc = schedule.__root__[0].line_name
        # ? if the next line name is different than the actual
        # ? and we don't placed 3 field in the row
        # ? then we add a invisble field
        if zz != cc and placed_field != 3:
            e.add_field(name=VOID_TOKEN, value=VOID_TOKEN)
            placed_field = 0

        # ? we need to reset the counter if we placed 3 row without invisible field
        if placed_field >= 3:
            placed_field = 0

    return e
