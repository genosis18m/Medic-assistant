
from fastmcp import FastMCP

# Import all tools
from tools.availability import check_availability
from tools.booking import (
    book_appointment,
    cancel_appointment,
    list_appointments
)
from tools.doctor_reports import (
    get_appointment_stats,
    get_patient_stats,
    generate_summary_report,
    send_slack_notification,
    send_report_to_telegram
)
from tools.patient_history import (
    get_patient_history,
    add_visit_notes,
    add_prescription,
    generate_patient_report
)
from tools.doctors import list_doctors

# Initialize FastMCP Server
mcp = FastMCP("Doctor Assistant")

# Register Tools
mcp.add_tool(check_availability)
mcp.add_tool(book_appointment)
mcp.add_tool(cancel_appointment)
mcp.add_tool(list_appointments)

mcp.add_tool(get_appointment_stats)
mcp.add_tool(get_patient_stats)
mcp.add_tool(generate_summary_report)
mcp.add_tool(send_slack_notification)
mcp.add_tool(send_report_to_telegram)

mcp.add_tool(get_patient_history)
mcp.add_tool(add_visit_notes)
mcp.add_tool(add_prescription)
mcp.add_tool(generate_patient_report)

mcp.add_tool(list_doctors)
