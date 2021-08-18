from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json


def update_if_exists(columnLetter, tag, valueType, jsonBlob, nextRow, worksheet):
    castTags = ["listing_price", "num_units", "taxes_annual", "insurance_expenses"]
    if jsonBlob[tag] != "0":
        if valueType != "":
            worksheet.format(
                columnLetter + nextRow, {"numberFormat": {"type": str(valueType)}}
            )
        worksheet.update(
            columnLetter + nextRow,
            int(jsonBlob[tag]) if tag in castTags else jsonBlob[tag],
        )
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

        update_if_exists("A", "address", "", row, next_row, worksheet)
        # worksheet.update("A" + next_row, row["address"])

        update_if_exists("B", "city", "", row, next_row, worksheet)
        # worksheet.update("B" + next_row, row["city"])

        update_if_exists("C", "style_code", "", row, next_row, worksheet)
        # worksheet.update("C" + next_row, row["style_code"])

        update_if_exists("D", "listing_price", "CURRENCY", row, next_row, worksheet)
        # worksheet.format("D" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        # worksheet.update("D" + next_row, int(row["listing_price"]))

        # create formula for down payment
        sale_price = worksheet.acell("D" + next_row).value
        # if sale_price != "MISSING":
        # worksheet.format(
        #   "E" + next_row, {"userEnteredFormat": {"formulaValue": "string"}}
        # )
        # worksheet.update("E" + next_row, "=D" + next_row + "*0.25")

        update_if_exists("G", "num_units", "NUMBER", row, next_row, worksheet)
        # worksheet.format("G" + next_row, {"numberFormat": {"type": "NUMBER"}})
        # worksheet.update("G" + next_row, int(row["num_units"]))

        worksheet.format("H" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        total_rent = 0
        for rent in row["units"]:
            total_rent += int(rent)
        worksheet.update("H" + next_row, total_rent)

        update_if_exists("Q", "taxes_annual", "CURRENCY", row, next_row, worksheet)
        # worksheet.format("Q" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        # worksheet.update("Q" + next_row, int(row["taxes_annual"]))

        update_if_exists(
            "R", "insurance_expenses", "CURRENCY", row, next_row, worksheet
        )
        # worksheet.format("R" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        # worksheet.update("R" + next_row, int(row["insurance_expenses"]))

        # update to next column
        next_row = str(int(next_row) + 1)
