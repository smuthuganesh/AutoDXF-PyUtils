import os
import ezdxf

def process_path(*paths):
    """Processes one or multiple DXF files, or all DXF files in a folder.

    Args:
        *paths: One or more paths to DXF files or folders containing DXF files.
    """
    dxf_files = []

    for path in paths:
        if os.path.isfile(path) and path.lower().endswith('.dxf'):
            # Add a single DXF file to the list
            dxf_files.append(path)
        elif os.path.isdir(path):
            # Add all DXF files in the folder to the list
            for filename in os.listdir(path):
                if filename.lower().endswith('.dxf'):
                    filepath = os.path.join(path, filename)
                    dxf_files.append(filepath)
        else:
            print(f"Invalid path: {path}. Please provide a valid DXF file or folder path.")
    
    # Process each DXF file found
    for dxf_file in dxf_files:
        print(f"\nProcessing {dxf_file}...")
        print(f"Filename: {os.path.basename(dxf_file)}")
        dxf_doc = load_dxf(dxf_file)
        display_details(dxf_doc)

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

def display_details(dxf_doc):
    list_doc(dxf_doc)
    list_headers(dxf_doc)
    list_layers(dxf_doc)
    list_blocks(dxf_doc)
    list_modelspace(dxf_doc)
    list_layouts(dxf_doc)
    list_others(dxf_doc)
    list_summary(dxf_doc)

def list_doc(dxf_doc):
    print(f"DXF Version: {dxf_doc.dxfversion}")
    print(f"Release: {dxf_doc.acad_release}")
    print(f"Encoding: {dxf_doc.encoding}")

def list_headers(dxf_doc, hide_zero=False, hide_empty=False):
    """Prints all header variables and their values from the DXF document.
    
    Args:
        dxf_doc: The DXF document object.
        hide_zero (bool): If True, hides variables with a zero value.
        hide_empty (bool): If True, hides variables with empty values.
    """
    print("\nHEADER Variables:")

    if(len(dxf_doc.header.varnames()) < 10):
        for key in dxf_doc.header.varnames():
            value = dxf_doc.header.get(key, 'Unknown')
            
            # Check for hiding conditions
            if hide_zero and value == 0:
                continue
            if hide_empty and value in ('', None):
                continue
            print(f"  {key}: {value}")
    else:
        print(f"    Too many to print (>9):")

def list_layers(dxf_doc):
    print("\nLayers:")
    for layer in dxf_doc.layers:
        print(f"  Layer Name: {layer.dxf.name}, Color: {layer.dxf.color}, Linetype: {layer.dxf.linetype}")

def list_blocks(dxf_doc):
    print("\nBlocks:")
    for block in dxf_doc.blocks:
        print(f"  Block Name: {block.name}, Entities: {len(block)}")

        if(len(block) < 10):
            for entity in block:
                layer = entity.dxf.layer if hasattr(entity.dxf, "layer") else "N/A"
                print(f"    Entity Type: {entity.dxftype()}, Layer: {layer}")
        else:
            print(f"    Too many to print (>9): Entity Type: , Layer: ")

def list_modelspace(dxf_doc):
    print("\nModelspace Entities:")
    modelspace = dxf_doc.modelspace()

    if(len(list(dxf_doc.modelspace())) < 10):
        for entity in modelspace:
            print(f"  Entity Type: {entity.dxftype()}, Layer: {entity.dxf.layer}")
    else:
        print(f"    Too many to print (>9): Entity Type: , Layer: ")

def list_layouts(dxf_doc):
    print("\nLayouts (Paper Space):")
    for layout in dxf_doc.layouts:
        if layout.name == 'Model':
            continue
        print(f"  Layout Name: {layout.name}")
        for entity in layout:
            print(f"    Entity Type: {entity.dxftype()}, Layer: {entity.dxf.layer}")

def list_others(dxf_doc):
    print("\nLinetypes:")
    for linetype in dxf_doc.linetypes:
        print(f"  Name: {linetype.dxf.name}, Description: {linetype.dxf.description}")

    print("\nText Styles:")
    for style in dxf_doc.styles:
        print(f"  Style Name: {style.dxf.name}")

    print("\nDimension Styles:")
    for dimstyle in dxf_doc.dimstyles:
        print(f"  Dimension Style: {dimstyle.dxf.name}")

def list_summary(dxf_doc):
    print("\nSummary:")
    print(f"  Total Header variables: {len(dxf_doc.header.varnames())}")
    print(f"  Total Layers: {len(dxf_doc.layers)}")
    print(f"  Total Blocks: {len(dxf_doc.blocks)}")
    print(f"  Total Modelspace: {len(list(dxf_doc.modelspace()))}")
    print(f"  Total Layouts: {len(dxf_doc.layouts) - 1}")  # Exclude modelspace
    print(f"  Total Linetypes: {len(dxf_doc.linetypes)}")
    print(f"  Total Text Styles: {len(dxf_doc.styles)}")
    print(f"  Total Dimension Styles: {len(dxf_doc.dimstyles)}")

if __name__ == "__main__":
    # Single DXF File:
    #   process_path("path/to/single.dxf")
    # Multiple DXF Files:
    #   process_path("path/to/file1.dxf", "path/to/file2.dxf")
    # Folder with DXF Files:
    #   process_path("path/to/folder")
    # Combination of Files and Folders:
    #   process_path("path/to/folder", "path/to/file1.dxf")

    #path = "/Users/smg/Documents/Programming/Code/python/latest/sampledxf/others/"
    path = "/Users/smg/Documents/Programming/Code/python/latest/sampledxf/others/now4.dxf"

    process_path(path)