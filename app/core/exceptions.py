from fastapi import HTTPException, status


class LeadNotFoundException(HTTPException):
    def __init__(self, lead_id: str, correlation_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "lead_not_found",
                    "message": "Заявка не найдена",
                    "correlation_id": correlation_id,
                }
            },
        )
