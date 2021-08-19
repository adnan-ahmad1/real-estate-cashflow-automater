from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json


def get_mortgage_formula(nextRow):
    return (
        "=IFS(C"
        + nextRow
        + ' = "Duplex", -1*PMT(0.0375/12, 30*12, F'
        + nextRow
        + "), C"
        + nextRow
        + ' = "Triplex", -1*PMT(0.0375/12, 30*12, F'
        + nextRow
        + "), C"
        + nextRow
        + ' = "4-Plex", -1*PMT(0.0375/12, 30*12, F'
        + nextRow
        + "), true, -1*PMT(0.04/12, 30*12, F"
        + nextRow
        + "))"
    )


def update_if_exists(columnLetter, valueType, value, nextRow, worksheet):
    if value is not None:
        if valueType != "":
            worksheet.format(
                columnLetter + nextRow, {"numberFormat": {"type": str(valueType)}}
            )
        worksheet.update(columnLetter + nextRow, value)
    else:
        worksheet.format(columnLetter + nextRow, {"backgroundColor": {"red": 0.5}})
        worksheet.update(columnLetter + nextRow, "MISSING")


def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list) + 1)


scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

client = gspread.authorize(creds)

worksheet = client.open("Real Estate Cashflow").sheet1

# extract data from json file
with open("cashflow/cashflow/cashflow.json", "r") as read_file:
    data = json.load(read_file)

    next_row = next_available_row(worksheet)
    for row in data:
        update_if_exists("A", "", row["address"], next_row, worksheet)
        update_if_exists("B", "", row["city"], next_row, worksheet)
        update_if_exists("C", "", row["style_code"], next_row, worksheet)
        update_if_exists(
            "D",
            "CURRENCY",
            int(row["listing_price"]) if row["listing_price"] != "0" else None,
            next_row,
            worksheet,
        )

        # create formula for down payment
        sale_price = worksheet.acell("D" + next_row).value
        if sale_price != "MISSING":
            worksheet.update(
                "E" + next_row,
                "=D" + next_row + "*0.25",
                value_input_option="USER_ENTERED",
            )

            worksheet.update(
                "F" + next_row,
                "=D" + next_row + "-E" + next_row,
                value_input_option="USER_ENTERED",
            )

        update_if_exists("G", "NUMBER", int(row["num_units"]), next_row, worksheet)

        worksheet.format("H" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        total_rent = 0
        for rent in row["units"]:
            total_rent += int(rent)
        update_if_exists("H", "CURRENCY", total_rent, next_row, worksheet)

        # enter mortgage formula
        worksheet.format("I" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        worksheet.update(
            "I" + next_row,
            get_mortgage_formula(next_row),
            value_input_option="USER_ENTERED",
        )

        # enter PM formula
        worksheet.format("J" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        worksheet.update(
            "J" + next_row,
            "=H" + next_row + "*0.12",
            value_input_option="USER_ENTERED",
        )

        # enter maintenance formula
        worksheet.format("M" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        worksheet.update(
            "M" + next_row,
            "=H" + next_row + "*0.05",
            value_input_option="USER_ENTERED",
        )

        # enter capital expenditure
        worksheet.format("N" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        worksheet.update(
            "N" + next_row,
            "=H" + next_row + "*0.05",
            value_input_option="USER_ENTERED",
        )

        update_if_exists(
            "Q",
            "CURRENCY",
            int(row["taxes_annual"]) if row["taxes_annual"] != "0" else None,
            next_row,
            worksheet,
        )

        update_if_exists(
            "R",
            "CURRENCY",
            int(row["insurance_expenses"])
            if row["insurance_expenses"] != "0"
            else None,
            next_row,
            worksheet,
        )

        # enter monthly tax formula
        worksheet.format("K" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        worksheet.update(
            "K" + next_row,
            "=Q" + next_row + "/12",
            value_input_option="USER_ENTERED",
        )

        # enter monthly insurance formula
        worksheet.format("L" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        worksheet.update(
            "L" + next_row,
            "=R" + next_row + "/12",
            value_input_option="USER_ENTERED",
        )

        # enter total expenses formula
        worksheet.format("O" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        worksheet.update(
            "O" + next_row,
            "=SUM(I" + next_row + ":N" + next_row + ")",
            value_input_option="USER_ENTERED",
        )

        # enter cash flow formula
        worksheet.format("P" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        worksheet.update(
            "P" + next_row,
            "=H" + next_row + "-O" + next_row,
            value_input_option="USER_ENTERED",
        )

        # update to next column
        next_row = str(int(next_row) + 1)
