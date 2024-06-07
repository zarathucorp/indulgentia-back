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
            "00": "Unauthorized",

            "10": "Unauthorized user access to User Setting",

            "20": "Unauthorized user access to Project",
            "21": "User is not in this project",
            "22": "User is not this project leader",

            "30": "Unauthorized user access to Bucket",
            "31": "User is not in this bucket",
            "32": "User is not this bucket owner",

            "40": "Unauthorized user access to Note",
            "41": "User is not in this note",
            "42": "User is not this note owner",

            "50": "Unauthorized user access to Team",
            "51": "User is not in this team",
            "52": "User is not this team leader",
            "53": "User is already in team",
            "54": "User is not in any team",
            "55": "Members still exist in this team",

            "60": "Unauthorized user access to Team Invite",
            "61": "User already accepted this team invite",
            "62": "User already rejected this team invite",
            "63": "Team invite request still exists",
        },

        # Forbidden
        "403": {
            "00": "Forbidden",

            "10": "Forbidden user access",
        },

        # Not found
        "404": {
            "00": "Not found",
        },

        # Unprocessable Entity
        "422": {
            "00": "Unprocessable Entity",

            "10": "Invalid Pydantic model",

            "20": "Invalid custom format",
            "21": "Invalid UUID format",
            "22": "Invalid email format",
            "23": "Invalid date format",
            "24": "Invalid file extension",
        },

        # Internal Server Error
        "500": {
            "00": "Internal Server Error",

            "10": "Python file system error",
            "11": "Python file write error",
            "12": "Python file read error",
            "13": "Python file delete error",

            "20": "Supabase Error",
            "21": "Supabase insert error",
            "22": "Supabase update error",
            "23": "Supabase single select error",
            "24": "Supabase multiple select error",
            "25": "Supabase delete error",
            "26": "Supabase RPC error",

            "30": "Azure Blob Storage Error",
            "31": "Azure Blob Storage upload error",
            "32": "Azure Blob Storage download error",

            "40": "PDF Generation Error",
            "41": "Introduction PDF Generation Error using FPDF2",
            "42": "Document PDF Generation Error using Libreoffice",
            "43": "Image PDF Generation Error using Pillow",
            "44": "PDF merge error",
            "45": "PDF sign error",

            "50": "Payment Error",
            "51": "Tosspayments API Error",

            "60": "Github API Error",
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
