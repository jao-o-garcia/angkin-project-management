"""MS Project XML export."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from xml.dom import minidom


def export_to_msproject_xml(
    schedule: list[dict],
    project_name: str = "Angkin Project",
    project_start: datetime | None = None,
) -> str:
    """Generate MS Project-compatible XML from schedule items.

    MS Project can import XML files following the Microsoft Project XML schema.
    This produces a simplified but functional XML that Project can open.
    """
    if project_start is None:
        project_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    root = ET.Element("Project", xmlns="http://schemas.microsoft.com/project")

    ET.SubElement(root, "Name").text = project_name
    ET.SubElement(root, "StartDate").text = project_start.strftime("%Y-%m-%dT08:00:00")
    ET.SubElement(root, "FinishDate").text = ""
    ET.SubElement(root, "CalendarUID").text = "1"

    # Calendar: 6-day work week (Mon-Sat), 8 hrs/day
    calendars = ET.SubElement(root, "Calendars")
    cal = ET.SubElement(calendars, "Calendar")
    ET.SubElement(cal, "UID").text = "1"
    ET.SubElement(cal, "Name").text = "PH Standard (6-day)"
    ET.SubElement(cal, "IsBaseCalendar").text = "1"

    week_days = ET.SubElement(cal, "WeekDays")
    for day_num in range(1, 8):  # 1=Sunday .. 7=Saturday
        wd = ET.SubElement(week_days, "WeekDay")
        ET.SubElement(wd, "DayType").text = str(day_num)
        if day_num == 1:  # Sunday off
            ET.SubElement(wd, "DayWorking").text = "0"
        else:
            ET.SubElement(wd, "DayWorking").text = "1"
            times = ET.SubElement(wd, "WorkingTimes")
            wt = ET.SubElement(times, "WorkingTime")
            ET.SubElement(wt, "FromTime").text = "08:00:00"
            ET.SubElement(wt, "ToTime").text = "17:00:00"

    # Tasks
    tasks_elem = ET.SubElement(root, "Tasks")

    for i, item in enumerate(schedule):
        task = ET.SubElement(tasks_elem, "Task")
        uid = i + 1
        ET.SubElement(task, "UID").text = str(uid)
        ET.SubElement(task, "ID").text = str(uid)
        ET.SubElement(task, "Name").text = f"[{item['trade'][:3].upper()}] {item['work_item']}"
        ET.SubElement(task, "Duration").text = _duration_to_iso(item["duration_days"])
        start = project_start + timedelta(days=item["start_day"] - 1)
        finish = project_start + timedelta(days=item["end_day"])
        ET.SubElement(task, "Start").text = start.strftime("%Y-%m-%dT08:00:00")
        ET.SubElement(task, "Finish").text = finish.strftime("%Y-%m-%dT17:00:00")
        ET.SubElement(task, "Work").text = _work_to_iso(item["adjusted_manhours"])

        if item.get("depends_on") and item["depends_on"].strip():
            pred_link = ET.SubElement(task, "PredecessorLink")
            try:
                pred_uid = int(item["depends_on"]) + 1
            except ValueError:
                pred_uid = uid - 1
            ET.SubElement(pred_link, "PredecessorUID").text = str(pred_uid)
            ET.SubElement(pred_link, "Type").text = "1"  # Finish-to-Start

    rough = ET.tostring(root, encoding="unicode", xml_declaration=True)
    return minidom.parseString(rough).toprettyxml(indent="  ")


def _duration_to_iso(days: float) -> str:
    """Convert working days to ISO 8601 duration (PT__H format for MS Project)."""
    hours = int(days * 8)
    return f"PT{hours}H0M0S"


def _work_to_iso(manhours: float) -> str:
    hours = int(manhours)
    return f"PT{hours}H0M0S"
