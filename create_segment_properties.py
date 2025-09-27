import json
import pandas as pd
from pathlib import Path
import argparse

def create_segment_properties(csv_path: Path | str, json_path: Path | str | None = None, print_segmentColors_for_viewer_json_state = True, exclude_segmentColors_from_properties = True):

    json_template = """
    {
        "@type": "neuroglancer_segment_properties",
        "inline": {
            "ids": [
            ],
            "properties": [
            ]
        }
    }
    """
    if isinstance(csv_path,str):
        csv_path = Path(csv_path)

    if json_path is None or (isinstance(json_path,str) and json_path == ""):
        json_path = csv_path.with_suffix(".json")
    elif isinstance(json_path,str):
        json_path = Path(json_path)

    df = pd.read_csv(csv_path,skiprows=2,header=0)

    with open(csv_path,mode="r") as f:
        # first line is types
        col_types_list = f.readline().replace("\n","").split(",")
        # second line is descriptions
        col_descriptions_list = f.readline().replace("\n","").split(",")
    col_names = list(df.columns)

    assert len(col_names) == len(col_types_list)
    assert len(col_names) == len(col_descriptions_list)

    col_types = {col_name: col_type for col_name, col_type in zip(col_names, col_types_list)}
    col_descriptions = {col_name: col_description for col_name, col_description in zip(col_names, col_descriptions_list)}
    df.head()
    segment_properties_info = json.loads(json_template)

    segment_properties_info
    segment_properties_info['inline']['ids'] = df["id"].astype(str).to_list()

    for col_name in df.columns:
        if col_name == "id":
            continue
        if print_segmentColors_for_viewer_json_state and col_name == "segmentColors":
            json_segmentColors = { id_seg: color_seg for id_seg, color_seg in zip(df["id"].astype(str).to_list(),df[col_name].astype(str).to_list()) }
            print("# Add this line to the segmentation layer in the viewer JSON state:\n","\"segmentColors\":", json.dumps(json_segmentColors))
        if exclude_segmentColors_from_properties and col_name == "segmentColors":
            continue
        properties_item = { 'id': col_name, 'type': col_types[col_name] }
        if col_types[col_name] == "number":
            # numeric_data_types = ["uint8", "int8", "uint16", "int16", "uint32", "int32", "float32"]
            if df[col_name].dtype.name == "int64":
                df[col_name] = df[col_name].astype("int32")
            if df[col_name].dtype.name == "float64":
                df[col_name] = df[col_name].astype("float32")
            properties_item['data_type'] = df[col_name].dtype.name
        if col_types[col_name] == "tags":
            # get all the possible values
            properties_item['tags'] = col_descriptions[col_name].split("|")
            # create an array of integers in ascending order that match the indices of previous array
            #  ...  but first, list all tags per row
            tags_all_rows = df[col_name].apply(lambda val: str(val).split("|")).to_list()
            #  ...  then create the corresponding list of arrays
            properties_item['values'] = [
                [i for i, tag in enumerate(properties_item['tags']) if tag in tags_single_row] 
                for tags_single_row in tags_all_rows
            ]
            # NB: setting 'tag_descriptions' is not supported, it can eventually be manually added
        else:
            properties_item['description'] = col_descriptions[col_name]
            properties_item['values'] = df[col_name].to_list()
        segment_properties_info['inline']['properties'].append(properties_item)

    with open(json_path,mode="w") as f:
        json.dump(segment_properties_info,f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a CSV into a segment_properties/info JSON file for Neuroglancer segmentation layers")
    parser.add_argument("csv_path", type=str, help="Path of the input CSV")
    parser.add_argument("json_path", type=str, help="Path of the output JSON")
    parser.add_argument("--print-segmentColors", help="Print in STDOUT the line to add to the viewer state for LUT control", action='store_true')
    parser.add_argument("--exclude-segmentColors", help="Exclude the \"segmentColors\" column from properties", action='store_true')
    
    args = parser.parse_args()

    create_segment_properties(args.csv_path, args.json_path, print_segmentColors_for_viewer_json_state=args.print_segmentColors, exclude_segmentColors_from_properties=args.exclude_segmentColors)