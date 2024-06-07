from fastapi import HTTPException


def custom_error(status_code: int, additional_code: int):
    if status_code < 100 or status_code > 999:
        raise Exception("status_code must be a three-digit number")
    if additional_code < 10 or additional_code > 99:
        raise Exception("additional_code must be a two-digit number")
    status_code_string = str(status_code)
    additional_code_string = str(additional_code)

    CUSTOM_CODE_DETAIL = {
        # Unauthorized
        "401": {

        },

        # Forbidden
        "403": {
            "10": "Forbidden user access",
        },

        # Not found
        "404": {
            "00": "Not found",
        },

        # Unprocessable Entity
        "422": {
            "10": "Invalid Pydantic model",
            "21": "Invalid UUID format",
            "22": "Invalid email format",
        },

        # Internal Server Error
        "500": {

        },
    }
    custom_code_string = status_code_string + additional_code_string

    if CUSTOM_CODE_DETAIL.get(status_code_string, None):
        if CUSTOM_CODE_DETAIL[status_code_string].get(additional_code_string, None):
            res = custom_code_string + " " + \
                CUSTOM_CODE_DETAIL[status_code_string][additional_code_string]
        else:
            res = custom_code_string + " Unknown error"
    else:
        res = custom_code_string + " Unknown error"

    raise HTTPException(status_code=status_code, detail=res)
