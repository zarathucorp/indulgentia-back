import re
from fastapi import HTTPException


def is_three_digit_number(s: str):
    return bool(re.match(r"^[0-9]{3}$", s))


def is_two_digit_number(s: str):
    return bool(re.match(r"^[0-9]{2}$", s))


def custom_error(status_code: str, additional_code: str):
    if not is_three_digit_number(status_code):
        raise Exception("status_code must be a three-digit number")
    if not is_two_digit_number(additional_code):
        raise Exception("additional_code must be a two-digit number")

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
    custom_code = status_code + additional_code

    if CUSTOM_CODE_DETAIL.get(status_code, None):
        if CUSTOM_CODE_DETAIL[status_code].get(additional_code, None):
            res = custom_code + " " + \
                CUSTOM_CODE_DETAIL[status_code][additional_code]
        else:
            res = custom_code + " Unknown error"
    else:
        res = custom_code + " Unknown error"

    raise HTTPException(status_code=int(status_code), detail=res)
