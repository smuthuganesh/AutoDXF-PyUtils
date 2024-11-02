import os
import time
import ezdxf
from ezdxf import colors
from ezdxf.enums import ACI

def duplicate_dxf(source_path, target_path, target_color):
    if os.path.abspath(os.path.normpath(source_path)) == os.path.abspath(os.path.normpath(target_path)):
        print(f"Error: Source and target paths are identical")
        return True

    print(f"\nProcessing {source_path}...")

    source_doc = load_dxf(source_path)
    file_metadata(source_path)
    display_details(source_doc)
  
    modify_color(source_doc, target_color)
    source_doc.saveas(target_path)
    print(f"Modified copy created at: {target_path}")

def load_dxf(filepath):
    try:        
        dxf_doc = ezdxf.readfile(filepath)
        return(dxf_doc)
    except IOError:
        print(f"Not a DXF file or a generic I/O error: {filepath}")
        return
    except ezdxf.DXFStructureError:
        print(f"Invalid or corrupted DXF file: {filepath}")
        return

def file_metadata(filepath):
    try:
        # Get file size
        file_size = os.path.getsize(filepath)

        # Get creation and last modified dates
        creation_time = os.path.getctime(filepath)
        last_modified_time = os.path.getmtime(filepath)

        # Format timestamps to readable format
        creation_date = time.ctime(creation_time)
        last_modified_date = time.ctime(last_modified_time)

        print(f"\nFile Metadata for {os.path.basename(filepath)}:")
        print(f"  File Size: {file_size} bytes")
        print(f"  Creation Date: {creation_date}")
        print(f"  Last Modified Date: {last_modified_date}")
    except Exception as e:
        print(f"Error retrieving file metadata: {e}")

def display_details(dxf_doc):
    list_doc(dxf_doc)
    annotations_color_distribution(dxf_doc)

def list_doc(dxf_doc):
    print("\ndxf Details:")
    print(f"  DXF Version: {dxf_doc.dxfversion}")
    print(f"  Release: {dxf_doc.acad_release}")
    print(f"  Encoding: {dxf_doc.encoding}")

def annotations_color_distribution(dxf_doc):
    """Lists all annotations (TEXT and MTEXT) and counts them."""
    annotations = []
    color_count = {}

    # Collect annotations in model space
    for entity in dxf_doc.modelspace():
        if entity.dxftype() in ('TEXT', 'MTEXT'):
            annotations.append(entity)
            color = entity.dxf.color
            if color not in color_count:
                color_count[color] = 0
            color_count[color] += 1

    # Collect annotations in paper space layouts
    for layout in dxf_doc.layouts:
        if layout.name != 'Model':
            for entity in layout:
                if entity.dxftype() in ('TEXT', 'MTEXT'):
                    annotations.append(entity)
                    color = entity.dxf.color
                    if color not in color_count:
                        color_count[color] = 0
                    color_count[color] += 1

    # Display and count annotations
    print(f"\nTotal Annotations (DText + MText): {len(annotations)}")
    print("\nColor Distribution:")
    for color, count in color_count.items():
        print(f"  Color {color}: {count} entities")

def modify_color(dxf_doc, target_color):
    modified_count = 0

    for mtext in dxf_doc.query('MTEXT'):
        if mtext.dxf.color != target_color:
            mtext.dxf.color = target_color
            modified_count += 1

    print(f"\n\nModified {modified_count} MTEXT entities")

def main():
    # Print basic ACI colors (1-7)
    for index in range(1, 8):
        color_name = ACI(index).name
        print(f"{index}: {color_name}")

if __name__ == "__main__":
    main()

    source_file = "/Users/smg/Documents/Programming/Code/python/sampledxf/kovai/1223.dxf"  # Replace with your source DXF file path
    target_file = "/Users/smg/Documents/Programming/Code/python/sampledxf/kovai/1223_out.dxf"  # Replace with your target DXF file path

    target_color = 3

    duplicate_dxf(source_file, target_file, target_color)