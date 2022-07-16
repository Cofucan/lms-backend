from fastapi import (
    APIRouter, 
    status, 
    HTTPException,
    Depends
)


router = APIRouter(prefix="/task")

@router.post(
    "/submit-task/",
    name="task:submit",
    status_code=status.HTTP_200_OK,
    response_model=TaskPublic,
    description="Submit a task."    
)
async def submit_task():
    pass 