import io
import base64
import os
from typing import Any, Dict, List
import httpx
import pandas as pd
from fastapi import HTTPException, status
import openpyxl


API_TOKEN = os.getenv("API_TOKEN", "")
EMAIL = os.getenv("EMAIL", "")
DOMAIN = os.getenv("DOMAIN", "")

async def fetch_jira_data() -> List[Dict[str, Any]]:
    """
    Asynchronously queries Jira Cloud REST API v3 using HTTPX.
    Uses Basic Auth (Email + API Token) and automatic query parameter encoding.
    """
    if not API_TOKEN or not EMAIL or not DOMAIN:
        raise ValueError("Missing required environment variables: API_TOKEN, EMAIL, or DOMAIN.")

    # Base64 authentication header setup
    auth_credentials = f"{EMAIL}:{API_TOKEN}"
    encoded_auth = base64.b64encode(auth_credentials.encode("utf-8")).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Construct JQL query
    jql_query = (
        'project IN ("USCS","APCS","USCRS") '
        'AND assignee IN membersOf(Sebpo) '
        'AND status IN ("In Progress", "QA In Progress", "Pause", "Prioritised", "Scoping", "Ready", "Resource Assigned") '
        'ORDER BY cf[23307] ASC, cf[27844] ASC, created DESC'
    )

    url = f"https://{DOMAIN}/rest/api/3/search/jql"
    params = {
        "jql": jql_query,
        "fields": "summary,assignee,status,customfield_29639,customfield_29783","timeSpent"
        "maxResults": 60
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("issues", [])
        except httpx.HTTPStatusError as http_err:
            print(f"❌ Jira API HTTP Error: {http_err.response.status_code} - {http_err.response.text}")
            raise HTTPException(
                status_code=http_err.response.status_code,
                detail=f"Jira API error: {http_err.response.text}"
            )
        except httpx.RequestError as req_err:
            print(f"❌ Connection Error: {req_err}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to reach Jira servers."
            )

def generate_jira_excel(issues: List[Dict[str, Any]]) -> io.BytesIO:
    """
    Parses raw Jira JSON issue records into a pandas DataFrame 
    and exports it to an in-memory Excel file (.xlsx).
    """
    rows = []
    for issue in issues:
        fields = issue.get("fields", {}) or {}
        assignee = fields.get("assignee") or {}
        status_obj = fields.get("status") or {}

        # Safely extract and convert Due Time to Bangladesh Time (BDT)
        raw_due_time = fields.get("customfield_29783", "") or ""
        due_time_bdt = format_to_bdt(raw_due_time)

        rows.append({
            "Jira ID": issue.get("key", ""),
            "Client": fields.get("customfield_29639", "") or "",
            "Due Time (BDT)": due_time_bdt,
            "Assignee": assignee.get("displayName", "") if isinstance(assignee, dict) else "",
            "Status": status_obj.get("name", "") if isinstance(status_obj, dict) else "",
            "Hour": "0"
        })

    # Convert list of rows to pandas DataFrame with specified column order
    df = pd.DataFrame(
        rows, 
        columns=["Jira ID", "Client", "Due Time (BDT)", "Assignee", "Status", "Hour"]
    )

    # Write DataFrame into memory buffer using openpyxl engine
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Jira Export")
    
    output.seek(0)
    return output

def format_to_bdt(raw_time_str: str) -> str:
    """
    Converts ISO 8601 UTC timestamp strings into Bangladesh Standard Time 
    (Asia/Dhaka, UTC+6) formatted as 'M/D/YYYY h:mm:ss AM/PM'.
    Example: '2026-08-05T13:00:00.000+0000' -> '8/5/2026 7:00:00 PM'
    """
    if not raw_time_str:
        return ""
    try:
        dt = pd.to_datetime(raw_time_str)
        if pd.isna(dt):
            return ""
        
        # Convert timezone to Asia/Dhaka (UTC+6)
        if dt.tz is None:
            dt = dt.tz_localize("UTC").tz_convert("Asia/Dhaka")
        else:
            dt = dt.tz_convert("Asia/Dhaka")
        
        # Format time with 12-hour clock AM/PM without leading zero in hour
        time_part = dt.strftime("%I:%M:%S %p").lstrip("0")
        return f"{dt.month}/{dt.day}/{dt.year} {time_part}"
    except Exception:
        return raw_time_str