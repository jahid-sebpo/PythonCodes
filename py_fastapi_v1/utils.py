import os
from typing import List, Dict, Any, Union
import pandas as pd

import io
import os
from typing import Any, Dict, List


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


def generate_excel(file_source, sheet_name, orient):
    data = read_excel(sheet_name, file_source, 'matrixfile.xlsx', orient)
    baseData = read_excel("baseData",None, "baseData.xlsx", "records")
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
    
    return output.getvalue();

def isBlank(d,s):
    if d == '' or d== 'NA' or d== 'nan' :
        return "blank.png"
    else:
        return f"{d}_{s}.png"


def read_excel(
        sheet_name,
        file_source: Union[str, io.BytesIO, None] = None,
        file_name: str = 'matrixfile.xlsx',
        orient: str = "records"
) -> Union[List[Dict[str, Any]], List[List[Any]]]:
    """
    Reads an Excel file either from a file path, raw bytes, or an in-memory binary stream (io.BytesIO),
    parses the specified sheet tab, and returns the data as a Python list/array.

    Parameters:
    - file_source (str | bytes | io.BytesIO | None): Input source. Defaults to file_folder/file_name if None.
    - sheet_name (str): Tab name to read inside the Excel workbook.
    - orient (str): Structure format ('records' for list of dicts, 'list' for 2D matrix array).
    - file_folder (str): Fallback directory path.
    - file_name (str): Fallback filename.

    Returns:
    - List containing extracted row data.
    """

    if file_source is None:
        file_source = os.path.join("file", file_name)

    # Convert BytesIO stream to raw bytes to safely evaluate length/sequence properties
    if isinstance(file_source, io.BytesIO):
        file_source = file_source.getvalue()

    # Distinguish string filepath vs binary buffer input
    if isinstance(file_source, str):
        if not os.path.exists(file_source):
            raise FileNotFoundError(f"Excel file not found at path: '{file_source}'")
        excel_input = file_source
    elif isinstance(file_source, bytes):
        excel_input = io.BytesIO(file_source)
    else:
        excel_input = file_source

    try:
        # Load excel data into pandas DataFrame
        df = pd.read_excel(excel_input, sheet_name=sheet_name)

        # Clean NaN/NaT values for JSON compatibility
        df = df.where(pd.notnull(df), None)

        if orient == "records":
            return df.to_dict(orient="records")
        elif orient == "list":
            headers = df.columns.tolist()
            rows = df.values.tolist()
            return [headers] + rows
        else:
            return df.to_dict(orient=orient)

    except ValueError as val_err:
        raise ValueError(f"Sheet '{sheet_name}' was not found in workbook. Details: {val_err}")
    except Exception as err:
        raise RuntimeError(f"Error parsing Excel file: {err}")
