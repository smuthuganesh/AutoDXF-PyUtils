import os
import time
import re
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

    print(f"\nModified copy created at: {target_path}")

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

def list_doc(dxf_doc):
    print("\ndxf Details:")
    print(f"  DXF Version: {dxf_doc.dxfversion}")
    print(f"  Release: {dxf_doc.acad_release}")
    print(f"  Encoding: {dxf_doc.encoding}")

def modify_color(dxf_doc, target_color):
    modified_count = 0
    modified_count_embeded = 0
    color_count = {}
    color_count_embeded = {}
    color_code_pattern = r'\\C(\d+);'
    replacement = f'\\C{target_color};'

    def collect_mtext_from_block(block):
        """Recursively collect MText entities from a block."""
        mtext_entities = []
        for entity in block:
            if entity.dxftype() == 'MTEXT':
                mtext_entities.append(entity)
            elif entity.dxftype() == 'INSERT':
                # If it's a block reference, collect MText from the referenced block
                referenced_block = dxf_doc.blocks.get(entity.dxf.name)
                if referenced_block:
                    mtext_entities.extend(collect_mtext_from_block(referenced_block))
        return mtext_entities
  
    # Initialize a list to store MText from all sources
    mtext_list = []

    # Collect MText from modelspace
    for entity in dxf_doc.modelspace():
        if entity.dxftype() == 'MTEXT':
            mtext_list.append(entity)

    # Collect MText from all layouts
    for layout in dxf_doc.layouts:
        for entity in layout:
            if entity.dxftype() == 'MTEXT':
                mtext_list.append(entity)

    # Collect MText from blocks
    for block in dxf_doc.blocks:
        mtext_list.extend(collect_mtext_from_block(block))

    # Remove duplicates
    mtext_list = list(set(mtext_list))
    
    for mtext in mtext_list:
        color = mtext.dxf.color
        if color not in color_count:
            color_count[color] = 0
        color_count[color] += 1

        if mtext.dxf.color != target_color:
            mtext.dxf.color = target_color
            modified_count += 1

        matches = re.finditer(color_code_pattern, mtext.text, re.IGNORECASE)
        for match in matches:
            color_embeded = match.group(1)
            if color_embeded not in color_count_embeded:
                color_count_embeded[color_embeded] = 0
            color_count_embeded[color_embeded] += 1

            if match.group(1) != target_color:
                mtext.text = mtext.text.replace(match.group(0), replacement)
                modified_count_embeded += 1

    print("\nColor Distribution:")
    for color, count in color_count.items():
        if color == target_color:
            print(f"  Color {color} (target color): {count} entities")
        else:
            print(f"  Color {color}: {count} entities")

    print("\nEmbeded Color Distribution:")
    for color, count in color_count_embeded.items():
        if color == target_color:
            print(f"  Color {color} (target color): {count} entities")
        else:
            print(f"  Color {color}: {count} entities")

    print(f"\nModified {modified_count} MTEXT entities")

    print(f"\nModified {modified_count_embeded} Embeded MTEXT entities")


def main():
    # Print ACI colors
    for index in range(256, 258):
        color_name = ACI(index).name
        print(f"{index}: {color_name}")
    for index in range(0, 10):
        color_name = ACI(index).name
        print(f"{index}: {color_name}")
    print("**7: BLACK on light background, WHITE on dark background")

if __name__ == "__main__":
    main()

    source_file = "/Users/smg/Documents/Programming/Code/python/sampledxf/kovai/1223.dxf"  # Replace with your source DXF file path
    target_file = "/Users/smg/Documents/Programming/Code/python/sampledxf/kovai/1223_out.dxf"  # Replace with your target DXF file path

    target_color = 3

    duplicate_dxf(source_file, target_file, target_color)
