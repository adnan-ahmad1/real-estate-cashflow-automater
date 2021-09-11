from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
import time

def get_mortgage_formula(nextRow):
    return (
        "=IFS(C"
        + nextRow
        + ' = "Duplex", -1*PMT(0.0375/12, 30*12, F'
        + nextRow
        + "), C"
        + nextRow
        + ' = "Tri-plex", -1*PMT(0.0375/12, 30*12, F'
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
        time.sleep(1)


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
        worksheet.update(
            "E" + next_row,
            "=D" + next_row + "*0.25",
            value_input_option="USER_ENTERED",
        )
        time.sleep(1)

        worksheet.update(
            "F" + next_row,
            "=D" + next_row + "-E" + next_row,
            value_input_option="USER_ENTERED",
        )
        time.sleep(1)

        # spread out units
        rents = row["units"]
        num_units = len(rents)

        worksheet.format("G" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        if 1 <= num_units:
            update_if_exists("G", "CURRENCY", int(rents[0]), next_row, worksheet)
            time.sleep(1)

        worksheet.format("H" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        if 2 <= num_units:
            update_if_exists("H", "CURRENCY", int(rents[1]), next_row, worksheet)
            time.sleep(1)

        worksheet.format("I" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        if 3 <= num_units:
            update_if_exists("I", "CURRENCY", int(rents[2]), next_row, worksheet)
            time.sleep(1)

        worksheet.format("J" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        if 4 <= num_units:
            update_if_exists("J", "CURRENCY", int(rents[3]), next_row, worksheet)
            time.sleep(1)

        worksheet.format("K" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        if 5 <= num_units:
            update_if_exists("K", "CURRENCY", int(rents[4]), next_row, worksheet)
            time.sleep(1)

        worksheet.format("L" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        if 6 <= num_units:
            i = 5
            rent_left_for_other_units = 0;
            while i < num_units:
                rent_left_for_other_units += int(rents[i])
                i = i + 1
            update_if_exists("L", "CURRENCY", rent_left_for_other_units, next_row, worksheet)
            time.sleep(1)

        worksheet.format("M" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        total_rent = 0
        for rent in row["units"]:
            total_rent += int(rent)
        update_if_exists("M", "CURRENCY", total_rent, next_row, worksheet)

        # enter mortgage formula
        worksheet.format("N" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        worksheet.update(
            "N" + next_row,
            get_mortgage_formula(next_row),
            value_input_option="USER_ENTERED",
        )
        time.sleep(1)

        # enter PM formula
        worksheet.format("O" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        worksheet.update(
            "O" + next_row,
            "=M" + next_row + "*0.12",
            value_input_option="USER_ENTERED",
        )
        time.sleep(1)

        # enter maintenance formula
        worksheet.format("R" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        worksheet.update(
            "R" + next_row,
            "=M" + next_row + "*0.05",
            value_input_option="USER_ENTERED",
        )
        time.sleep(1)

        # enter capital expenditure
        worksheet.format("S" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        worksheet.update(
            "S" + next_row,
            "=M" + next_row + "*0.05",
            value_input_option="USER_ENTERED",
        )
        time.sleep(1)

        # enter annual taxes
        update_if_exists(
            "V",
            "CURRENCY",
            int(row["taxes_annual"]) if row["taxes_annual"] != "0" else None,
            next_row,
            worksheet,
        )

        # enter insurance expenses
        update_if_exists(
            "W",
            "CURRENCY",
            int(row["insurance_expenses"])
            if row["insurance_expenses"] != "0"
            else None,
            next_row,
            worksheet,
        )

        # enter monthly tax formula
        worksheet.format("P" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        worksheet.update(
            "P" + next_row,
            "=V" + next_row + "/12",
            value_input_option="USER_ENTERED",
        )
        time.sleep(1)

        # enter monthly insurance formula
        worksheet.format("Q" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        worksheet.update(
            "Q" + next_row,
            "=W" + next_row + "/12",
            value_input_option="USER_ENTERED",
        )
        time.sleep(1)

        # enter total expenses formula
        worksheet.format("T" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        worksheet.update(
            "T" + next_row,
            "=SUM(N" + next_row + ":S" + next_row + ")",
            value_input_option="USER_ENTERED",
        )
        time.sleep(1)

        # enter cash flow formula
        worksheet.format("U" + next_row, {"numberFormat": {"type": "CURRENCY"}})
        time.sleep(1)
        worksheet.update(
            "U" + next_row,
            "=M" + next_row + "-T" + next_row,
            value_input_option="USER_ENTERED",
        )
        time.sleep(1)

        # update to next column
        next_row = str(int(next_row) + 1)
