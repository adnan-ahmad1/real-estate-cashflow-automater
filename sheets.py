from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json


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
        worksheet.update("A" + next_row, row["address"])
        worksheet.update("B" + next_row, row["city"])
        worksheet.update("C" + next_row, row["style_code"])
        worksheet.update("D" + next_row, int(row["listing_price"]))
        worksheet.update("G" + next_row, int(row["num_units"]))

        total_rent = 0
        for rent in row["units"]:
            total_rent += int(rent)
        worksheet.update("H" + next_row, total_rent)

        worksheet.update("Q" + next_row, int(row["taxes_annual"]))
        worksheet.update("R" + next_row, int(row["insurance_expenses"]))

        # update to next column
        next_row = str(int(next_row) + 1)
