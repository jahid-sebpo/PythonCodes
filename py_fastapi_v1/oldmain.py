import io
import os
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException, status
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from dotenv import load_dotenv

import jiraHandler,utils

load_dotenv()


app = FastAPI(
    title="Automation",
)

@app.get("/")
def read_root():
    return "Api is running..."


@app.get("/jiraData", response_model=List[Dict[str, Any]])
async def get_jira_data():
    """
    Endpoint to retrieve Jira tickets matching the specified JQL query.
    """
    try:
        issues = await jiraHandler.fetch_jira_data()
        return issues
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(val_err)
        )
    except HTTPException:
        raise
    except Exception as err:
        print(f"❌ Unexpected Error: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching Jira data."
        )


@app.get("/jiraData/excel")
async def get_jira_excel():
    """
    Endpoint to download the prioritized Jira tickets as an Excel (.xlsx) file.
    """
    try:
        issues = await jiraHandler.fetch_jira_data()
        excel_stream = jiraHandler.generate_jira_excel(issues)
        
        headers = {
            "Content-Disposition": "attachment; filename=jira_issues_export.xlsx"
        }
        
        return StreamingResponse(
            excel_stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(val_err)
        )
    except HTTPException:
        raise
    except Exception as err:
        print(f"❌ Unexpected Error: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating Excel file."
        )
  
@app.post("/upload-excel")
async def upload_excel(
    file: UploadFile = File(...),
    sheet_name: str = Form("FT Matrix Output"),
    orient: str = Form("records")
):
    """
    Accepts an uploaded Excel file (.xlsx or .xls) as multipart form data,
    reads the requested tab in memory, and returns the parsed rows as JSON.
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload an Excel file (.xlsx or .xls)."
        )
    try:
        # Read raw binary contents directly from request stream
        file_bytes = await file.read()
        
        # Parse matrix data from byte stream
        excel_bytes = utils.generate_excel(
            file_source=file_bytes,
            sheet_name=sheet_name,
            orient=orient
        )
        headers = {
            "Content-Disposition": "attachment; filename=optimumOutput.xlsx"
        }
        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(val_err)
        )
    except HTTPException:
        raise
    except Exception as err:
        print(f"❌ Unexpected Error: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating Excel file."
        )


@app.get("/view", response_class=HTMLResponse)
async def serve_index():
    """
    Serves the primary user interface HTML page.
    """
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Matrix Excel Processor API Running</h1><p>index.html not found in root directory.</p>"
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)