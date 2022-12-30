from pathlib import Path 
from openpyxl import load_workbook

Constans_DNV_folder_path = Path(__file__).parent
Constans_DNV_file_path = Constans_DNV_folder_path.parent / "Data_input/Constants_DNV.xlsx"


# Loading factors DNV 
wb_factors_dnv = load_workbook(Constans_DNV_file_path)
Fact_names = wb_factors_dnv.sheetnames

Fact_text = {}
Fact_values = {}
for factor in Fact_names:
    # Getting worksheet 
    ws=wb_factors_dnv[factor]
    # Starting at row 2 see excel
    i=2
    text_values = []
    text="a"
    row_factors = {}

    while text!=None:
        text=ws["A"+str(i)].value
        if text!=None:
            # Daf is other type of data storage see Excel
            if factor == "DAF":
                text_values = ["Offshore","Inshore"]
                row_factors[text] = [ws["B"+str(i)].value,
                                    ws["C"+str(i)].value]
            else:
                row_factors[text] = ws["B"+str(i)].value
                
                text_values.append(text)
            i+=1
    Fact_values[factor] = row_factors
    Fact_text[factor] = text_values



Table_Lift_points=[{"point":"A","x":0,"y":0,"z":0},
                    {"point":"B","x":0,"y":0,"z":0},
                    {"point":"C","x":0,"y":0,"z":0},
                    {"point":"D","x":0,"y":0,"z":0} ]
