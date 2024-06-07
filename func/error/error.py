from fastapi import HTTPException


def custom_error(status_code: int, additional_code: int):
    CUSTOM_CODE_DETAIL = {
        # Unauthorized
        401: {

        },

        # Forbidden
        403: {
            10: "Forbidden user access",
        },

        # Not found
        404: {
            00: "Not found",
        },

        # Unprocessable Entity
        422: {
            10: "Invalid Pydantic model",
            21: "Invalid UUID format",
            22: "Invalid email format",
        },

        # Internal Server Error
        500: {

        },
    }
    custom_code = str(status_code) + str(additional_code)

    raise HTTPException(status_code=status_code, detail=custom_code +
                        CUSTOM_CODE_DETAIL[status_code][custom_code] if custom_code in CUSTOM_CODE_DETAIL[status_code] else "Unknown error")
