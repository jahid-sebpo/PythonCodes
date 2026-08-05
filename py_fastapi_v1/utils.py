import os
from typing import List, Dict, Any, Union
import pandas as pd

import io
import os
from typing import Any, Dict, List


def read_excel(
    file_folder: str = "file",
    file_name: str = "matrixfile.xlsx",
    sheet_name: str = "FT Matrix Output",
    orient: str = "records"
) -> Union[List[Dict[str, Any]], List[List[Any]]]:
    """
    Reads an Excel file named 'matrixfile' from the 'file' folder and reads 
    the 'matrix sheet' tab, returning the data as a Python array (list).

    Parameters:
    - file_folder (str): Directory where the Excel file is located. Default is 'file'.
    - file_name (str): Filename with extension. Default is 'matrixfile.xlsx'.
    - sheet_name (str): Tab name to read. Default is 'matrix sheet'.
    - orient (str): Output array format:
        * 'records' (default): Returns list of row dicts -> [{'Col1': 'Val1', 'Col2': 'Val2'}, ...]
        * 'list': Returns 2D array including header -> [['Col1', 'Col2'], ['Val1', 'Val2'], ...]

    Returns:
    - List containing the sheet records/rows.
    """
    # Build complete path to the file
    file_path = os.path.join(file_folder, file_name)

    # Check if the file exists before attempting to read
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ Excel file not found at path: '{file_path}'")

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Replace NaN / None values with empty string or None for clean representation
        df = df.where(pd.notnull(df), None)

        if orient == "records":
            # Returns array of dictionaries
            return df.to_dict(orient="records")
        elif orient == "list":
            # Returns 2D array (rows & columns)
            headers = df.columns.tolist()
            rows = df.values.tolist()
            return rows
            return "[headers] + rows[0]"
        else:
            return df.to_dict(orient=orient)

    except ValueError as val_err:
        raise ValueError(f"❌ Sheet '{sheet_name}' was not found in '{file_name}'. Details: {val_err}")
    except Exception as err:
        raise RuntimeError(f"❌ Error reading Excel file '{file_path}': {err}")

def debug():
    data = read_excel()
    generate_excel(data)


def legalHandler(l):
    TA = ["Terms apply.", "See details"]  # Can be a string, list, tuple, or set
    # 1. Clean the outer whitespace first
    if not l: 
        return ""
    legal = l.strip()

    # 2. Normalize TA into a list of strings
    if isinstance(TA, str):
        ta_list = [TA]
    elif isinstance(TA, (list, tuple, set)):
        ta_list = [str(item) for item in TA]
    else:
        ta_list = [str(TA)]

    # 3. Sort items by length (longest first) to prevent partial replacement bugs
    # (e.g., replacing 'apple' inside 'pineapple' by mistake)
    ta_list.sort(key=len, reverse=True)

    # 4. Perform the replacements sequentially
    for item in ta_list:
        if item:  # Skip empty strings
            legal = legal.replace(item, f"<span class='underline'>{item}</span>")
            return legal


def generate_excel():
    data = read_excel("file", "matrixfile.xlsx","FT Matrix Output","records")
    baseData = read_excel("file", "baseData.xlsx","baseData","records")

    rows = []
    i = 0
    while i < 4:
        for d in data:
            f1_legal = legalHandler(d.get("f1_legal_DESKTOP", {}) or {})
            f2_legal = legalHandler(d.get("f2_legal DESKTOP", {}) or {})
            f3_legal = legalHandler(d.get("f3_legal_DESKTOP", {}) or {})
            legalPanel = legalHandler(d.get("legalPanel : Text (expanded full frame)", {}) or {})
            legal = "|".join(filter(None, [f1_legal, f2_legal, f3_legal]))
            
            rows.append({
                "Creative File Name": f"_{baseData[i]["size"]}.zip",
                "Version Name": d.get("Version Name", {}) or {},
                "feed_endpoint : Text":"", 
                "layout_toggle : Text": baseData[i]["layout_toggle : Text"], 
                "frame_count_toggle : Text": d.get("frame_count_toggle : Text", {}) or {},
                "f1_subheadline_txt : Text":"", 
                "f1subheadline_size_hex_weight_xy : Text": baseData[i]["f1subheadline_size_hex_weight_xy : Text"], 
                "f1_headline_txt : Text": d.get("F1_headline_txt : Text (Claim) DESKTOP", {}) or {},
                "f1headline_size_hex_weight_xy : Text": baseData[i]["f1headline_size_hex_weight_xy : Text"], 
                "f2_subheadline_txt : Text":"", 
                "f2subheadline_size_hex_weight_xy : Text": baseData[i]["f2subheadline_size_hex_weight_xy : Text"], 
                "f2_headline_txt : Text": d.get("F2_headline_txt : Text (Offer) DESKTOP", {}) or {}, 
                "f2headline_size_hex_weight_xy : Text": baseData[i]["f2headline_size_hex_weight_xy : Text"], 
                "f3_subheadline_txt : Text":"", 
                "f3subheadline_size_hex_weight_xy : Text": baseData[i]["f3subheadline_size_hex_weight_xy : Text"], 
                "f3_headline_txt : Text":"", 
                "f3headline_size_hex_weight_xy : Text": baseData[i]["f3headline_size_hex_weight_xy : Text"], 
                "legal_text : Text": legal, 
                "legal_size_hex_weight_xy : Text": baseData[i]["legal_size_hex_weight_xy : Text"], 
                "legalPanel : Text": legalPanel, 
                "legalPanel_size_hex_weight_xy : Text": baseData[i]["legalPanel_size_hex_weight_xy : Text"], 
                "cta_txt : Text": d.get("cta_txt : Text", {}) or {}, 
                "cta_txt_size_hex_hexHover_weight_xy : Text": baseData[i]["cta_txt_size_hex_hexHover_weight_xy : Text"], 
                "cta_bgHex_bgHexHover : Text": baseData[i]["cta_bgHex_bgHexHover : Text"], 
                "offer_hex_weight_strike_hex_thickness_bullet_hex_size : Text": baseData[i]["offer_hex_weight_strike_hex_thickness_bullet_hex_size : Text"], 
                "frame1_img : Image": isBlank( d.get("f1_background_img : Image", {}), baseData[i]["size"]),
                "frame2_img : Image": isBlank( d.get("f2_background_img : Image", {}), baseData[i]["size"]),
                "frame3_img : Image": isBlank( d.get("f3_background_img : Image", {}), baseData[i]["size"]),
                "logo_img : Image":isBlank("",baseData[i]["size"]), 
                "logoimg_height_width_xy : Text": baseData[i]["logoimg_height_width_xy : Text"], 
                "background_pattern_img : Image": baseData[i]["background_pattern_img : Image"], 
                "f1_vendor_img : Image": baseData[i]["f1_vendor_img : Image"], 
                "f2_vendor_img : Image": baseData[i]["f2_vendor_img : Image"], 
                "f3_vendor_img : Image": baseData[i]["f3_vendor_img : Image"], 
                "f1_vendorimg_height_width_xy_f2_vendorimg_height_width_xy_f3_vendorimg_height_width_xy : Text": baseData[i]["f1_vendorimg_height_width_xy_f2_vendorimg_height_width_xy_f3_vendorimg_height_width_xy : Text"], 
                "background_color : Text":"", 
                "background_img : Image": baseData[i]["background_img : Image"], 
                "feedfail_img : Image": baseData[i]["feedfail_img : Image"], 
                "clickTag_url : Text": d.get("clickTag_url : Text (Destination URL)", {}) or {}, 
                "richload : Richload": baseData[i]["richload : Richload"], 
            })
        i+=1
    # Convert list of rows to pandas DataFrame with specified column order
    df = pd.DataFrame(
        rows, 
        columns=["Creative File Name", "Version Name", "feed_endpoint : Text", "layout_toggle : Text", "frame_count_toggle : Text", "f1_subheadline_txt : Text", "f1subheadline_size_hex_weight_xy : Text", "f1_headline_txt : Text", "f1headline_size_hex_weight_xy : Text", "f2_subheadline_txt : Text", "f2subheadline_size_hex_weight_xy : Text", "f2_headline_txt : Text", "f2headline_size_hex_weight_xy : Text", "f3_subheadline_txt : Text", "f3subheadline_size_hex_weight_xy : Text", "f3_headline_txt : Text", "f3headline_size_hex_weight_xy : Text", "legal_text : Text", "legal_size_hex_weight_xy : Text", "legalPanel : Text", "legalPanel_size_hex_weight_xy : Text", "cta_txt : Text", "cta_txt_size_hex_hexHover_weight_xy : Text", "cta_bgHex_bgHexHover : Text", "offer_hex_weight_strike_hex_thickness_bullet_hex_size : Text", "frame1_img : Image", "frame2_img : Image", "frame3_img : Image", "logo_img : Image", "logoimg_height_width_xy : Text", "background_pattern_img : Image", "f1_vendor_img : Image", "f2_vendor_img : Image", "f3_vendor_img : Image", "f1_vendorimg_height_width_xy_f2_vendorimg_height_width_xy_f3_vendorimg_height_width_xy : Text", "background_color : Text", "background_img : Image", "feedfail_img : Image", "clickTag_url : Text", "richload : Richload"]
    )
    # Write DataFrame into memory buffer using openpyxl engine
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="OptimumBase")
    
    output.seek(0)
    return output

def isBlank(d,s):
    if d == '' or d== 'NA' or d== 'nan' :
        return "blank.png"
    else:
        return f"{d}_{s}.png"