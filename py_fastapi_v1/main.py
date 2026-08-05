from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

import jiraHandler,utils

load_dotenv()


app = FastAPI(
    title="Jira Data Integration API",
)

@app.get("/")
def read_root():
    return "Api is running..."


# Updating

@app.get("/optimum")
def debug():
    try:
        excel_stream = utils.generate_excel()
        
        headers = {
            "Content-Disposition": "attachment; filename=optimumOutput.xlsx"
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



# Update Done  


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

    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)