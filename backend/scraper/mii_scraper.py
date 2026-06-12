from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo
import requests
import os
from openpyxl.utils import get_column_letter

def autofit_columns(ws):
    for column in ws.columns:
        max_length = max(
            (len(str(cell.value)) for cell in column if cell.value is not None),
            default=0
        )
        ws.column_dimensions[
            get_column_letter(column[0].column)
        ].width = max_length + 2

class MIIScraper:
    def __init__(self, url, custom_name = ''):
        self.url = url
        self.name = custom_name if custom_name else url.split("-")[-1].split(".html")[0]

    def create_excel(self, savefolder=''):
        file_name = f"FHIR_Module_Description_{self.name}.xlsx"

        current_file_path = os.path.abspath(__file__)
        file_path = os.path.join(savefolder, file_name) if savefolder else os.path.join(current_file_path, "..", "scrapedFiles", file_name)

        HEADERVALUES = ["HL7_Values", self.name, "Type", "Kardinalität", "Notizen", "fixedValues"]
        NAME_COL, TYPE_COL, CARDINALITY_COL = [HEADERVALUES.index(x)+1 for x in [self.name, "Type", "Kardinalität"]] 


        red_fill = PatternFill(fill_type="solid", start_color="FF0000", end_color="FF0000")
        grey_fill = PatternFill(fill_type="solid", start_color="A6A6A6", end_color="A6A6A6")

        response = requests.get(self.url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        panel = soup.select_one("div.treetable-left-panel")
        if not panel:
            raise Exception("Kein div mit Klasse 'treetable-left-panel' gefunden.")

        table = panel.select_one("table.treetable")
        if not table:
            raise Exception(
                "Keine Tabelle mit Klasse 'treetable' innerhalb von '.treetable-left-panel' gefunden."
            )

        wb = Workbook()
        ws = wb.active
        ws.title = self.name

        # Header
        for i, headervalue in enumerate(HEADERVALUES):
            ws.cell(row=1, column=i+1, value=headervalue)
            ws.cell(row=2, column=i+1).fill = PatternFill(fill_type="solid", start_color="CCCCCC", end_color="CCCCCC")

        excel_row = 3

        for row in table.select("tr.constraints"):
            row_id = row.get("id")

            # Alle td der Zeile holen
            tds = row.find_all("td")

            if len(tds) >= 3:
                # Drittes td (Index 2)
                cardinality = tds[2].get_text(strip=True)
            if len(tds) >= 4:
                # Viertes td (Index 3)
                datatype = tds[3].get_text(strip=True).split("(")[0]

            if row_id:
                ws.cell(row=excel_row, column=NAME_COL, value=row_id)
                if cardinality.startswith("1"):
                    ws.cell(row=excel_row, column=CARDINALITY_COL, value=cardinality).fill = red_fill
                else:
                    ws.cell(row=excel_row, column=CARDINALITY_COL, value=cardinality)
                ws.cell(row=excel_row, column=TYPE_COL, value=datatype)
                excel_row += 1
        
        # Make every entry grey which has a child
        last_value = ""
        for row_num in range(excel_row-1, 1, -1):  # von letzter Datenzeile bis Zeile 2
            value = ws.cell(row=row_num, column=NAME_COL).value

            #Check if last_value is a child of Value
            if value and last_value.startswith(value):
                ws.cell(row=row_num, column=NAME_COL).fill = grey_fill

            last_value = value
        
        with open(os.path.join(current_file_path, "..", "scrapedFiles", f"{self.name}_whiteValues.txt"), 'w', encoding='utf-8') as tf:
            tf.write("NON GREY COLUMNS:\n\n")
            for row_num in range(2, excel_row):
                tf_name = ws.cell(row=row_num, column=NAME_COL).value
                tf_type = ws.cell(row=row_num, column=TYPE_COL).value
                tf_cardinality = ws.cell(row=row_num, column=CARDINALITY_COL).value
                color = ws.cell(row=row_num, column=NAME_COL).fill.start_color.rgb
                if color == "00000000":
                    tf.write(f"{tf_name} -> {tf_type} : {tf_cardinality}\n")
        
        autofit_columns(ws)

        # Create table
        last_row = excel_row - 1  # weil excel_row bei dir immer +1 weiterläuft
        table_range = f"A1:{chr(64+len(HEADERVALUES))}{last_row}"
        tab = Table(
            displayName="ConstraintsTable",
            ref=table_range
        )
        style = TableStyleInfo(
            name="TableStyleMedium2",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False
        )

        tab.tableStyleInfo = style
        ws.add_table(tab)

        wb.save(file_path)

        print(f"{excel_row - 2} IDs gespeichert.")

miiScraper = MIIScraper(url = "https://www.medizininformatik-initiative.de/Kerndatensatz/KDS_Medikation_2026/MIIIGModulMedikation-TechnischeImplementierung-FHIR-Profile-MedicationStatement.html")
miiScraper.create_excel()


