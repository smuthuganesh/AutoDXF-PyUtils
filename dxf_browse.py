import os
import time
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
        file_metadata(dxf_file)
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
    list_headers(dxf_doc, max=10)
    list_layers(dxf_doc)
    list_blocks(dxf_doc, max=10)
    list_modelspace(dxf_doc, max=10)
    list_layouts(dxf_doc)
    list_viewports(dxf_doc)
    class_count = list_classes(dxf_doc, max=10)
    list_objects(dxf_doc, max=10)
    color_distribution(dxf_doc)
    list_annotations(dxf_doc)
    list_others(dxf_doc)
    list_summary(dxf_doc, class_count)

def list_doc(dxf_doc):
    print("\ndxf Details:")
    print(f"  DXF Version: {dxf_doc.dxfversion}")
    print(f"  Release: {dxf_doc.acad_release}")
    print(f"  Encoding: {dxf_doc.encoding}")

def list_headers(dxf_doc, max=10, hide_zero=False, hide_empty=False):
    """Prints all header variables and their values from the DXF document.
    Args:
        dxf_doc: The DXF document object.
        hide_zero (bool): If True, hides variables with a zero value.
        hide_empty (bool): If True, hides variables with empty values.
    """
    print("\nHEADER Variables:")

    if(len(dxf_doc.header.varnames()) < max):
        for key in dxf_doc.header.varnames():
            value = dxf_doc.header.get(key, 'Unknown')
            
            # Check for hiding conditions
            if hide_zero and value == 0:
                continue
            if hide_empty and value in ('', None):
                continue
            print(f"  {key}: {value}")
    else:
        print(f"    Too many to print ({max}):")

def list_layers(dxf_doc):
    print("\nLayers:")
    for layer in dxf_doc.layers:
        print(f"  Layer Name: {layer.dxf.name}, Color: {layer.dxf.color}, Linetype: {layer.dxf.linetype}")

def list_blocks(dxf_doc, max=10):
    print("\nBlocks:")
    for block in dxf_doc.blocks:
        print(f"  Block Name: {block.name}, Entities: {len(block)}")

        if(len(block) < max):
            for entity in block:
                layer = entity.dxf.layer if hasattr(entity.dxf, "layer") else "N/A"
                print(f"    Entity Type: {entity.dxftype()}, Layer: {layer}")
        else:
            print(f"    Too many to print ({max}): Entity Type: , Layer: ")

def list_modelspace(dxf_doc, max=10):
    print("\nModelspace Entities:")
    modelspace = dxf_doc.modelspace()

    if(len(list(dxf_doc.modelspace())) < max):
        for entity in modelspace:
            print(f"  Entity Type: {entity.dxftype()}, Layer: {entity.dxf.layer}")
    else:
        print(f"    Too many to print ({max}): Entity Type: , Layer: ")

def list_layouts(dxf_doc):
    print("\nLayouts (Paper Space):")
    for layout in dxf_doc.layouts:
        if layout.name == 'Model':
            continue
        print(f"  Layout Name: {layout.name}")
        for entity in layout:
            print(f"    Entity Type: {entity.dxftype()}, Layer: {entity.dxf.layer}")

def list_viewports(dxf_doc):
    print("\nViewports:")
    for viewport in dxf_doc.viewports:
        print(f"  Viewport Name: {viewport.dxf.name}, Center: {viewport.dxf.center}, Height: {viewport.dxf.height}")

def list_classes(dxf_doc, max=10):
    print("\nClasses:")
    class_count = 0
    for cls in dxf_doc.classes:
        class_count += 1

    if(class_count < max):
        for cls in dxf_doc.classes:
            name = getattr(cls.dxf, "name", "N/A")
            version = getattr(cls.dxf, "version", "N/A")
            app_name = getattr(cls.dxf, "appname", "N/A")
            print(f"  Class Name: {name}, Version: {version}, Application Name: {app_name}")
    else:
        print(f"    Too many to print ({max}): Class Name: , Version: , Application Name: ")

    return(class_count)

def list_objects(dxf_doc, max=10):
    print("\nObjects:")
    if(len(dxf_doc.objects) < max):
        for obj in dxf_doc.objects:
            print(f"  Object Type: {obj.dxftype()}, Handle: {obj.dxf.handle}")
            if obj.dxftype() == "DICTIONARY":
                print(f"    Dictionary Owner: {obj.dxf.owner}")
                print(f"    Number of Entries: {len(obj)}")
                for key, value in obj.items():
                    print(f"      Key: {key}, Value Handle: {value.dxf.handle}")
            elif obj.dxftype() == "LAYOUT":
                print(f"    Layout Name: {obj.dxf.name}, Tab Order: {obj.dxf.taborder}")
            elif obj.dxftype() == "MLINESTYLE":
                style_name = getattr(obj.dxf, "style_name", "N/A")
                description = getattr(obj.dxf, "description", "N/A")
                print(f"    Style Name: {style_name}, Description: {description}")
    else:
        print(f"    Too many to print ({max}): Style Name: , Description: ")

def color_distribution(dxf_doc):
    color_count = {}
    # Check entities in model space
    for entity in dxf_doc.modelspace():
        color = entity.dxf.color
        if color not in color_count:
            color_count[color] = 0
        color_count[color] += 1

    # Include entities in layouts
    for layout in dxf_doc.layouts:
        if layout.name != 'Model':
            for entity in layout:
                color = entity.dxf.color
                if color not in color_count:
                    color_count[color] = 0
                color_count[color] += 1

    print("\nColor Distribution:")
    for color, count in color_count.items():
        print(f"  Color {color}: {count} entities")

def list_annotations(dxf_doc):
    """Lists all annotations (TEXT and MTEXT) and counts them."""
    annotations = []

    # Collect annotations in model space
    for entity in dxf_doc.modelspace():
        if entity.dxftype() in ('TEXT', 'MTEXT'):
            annotations.append(entity)

    # Collect annotations in paper space layouts
    for layout in dxf_doc.layouts:
        if layout.name != 'Model':
            for entity in layout:
                if entity.dxftype() in ('TEXT', 'MTEXT'):
                    annotations.append(entity)

    # Display and count annotations
    print(f"\nTotal Annotations (DText + MText): {len(annotations)}")

    if annotations:
        print("\nAnnotations:")
        for entity in annotations:
            # Common properties for TEXT and MTEXT
            text_content = entity.dxf.text if entity.dxftype() == "TEXT" else entity.text
            insertion_point = entity.dxf.insert
            layer = entity.dxf.layer
            print(f"  Type: {entity.dxftype()}, Text: '{text_content}', "
                  f"Insertion Point: {insertion_point}, Layer: {layer}")

def list_others(dxf_doc):
    print("\nLinetypes:")
    for linetype in dxf_doc.linetypes:
        print(f"  Name: {linetype.dxf.name}, Description: {linetype.dxf.description}")

    print("\nText Styles:")
    for textstyle in dxf_doc.styles:
        height = getattr(textstyle.dxf, "fixed_height", "N/A")
        width_factor = getattr(textstyle.dxf, "width", "N/A")
        print(f"  TextStyle Name: {textstyle.dxf.name}, Height: {height}, Width Factor: {width_factor}")

    print("\nDimension Styles:")
    for dimstyle in dxf_doc.dimstyles:
        print(f"  DimStyle Name: {dimstyle.dxf.name}, DimScale: {dimstyle.dxf.dimasz}")

def list_summary(dxf_doc, class_count):
    print("\nSummary:")
    print(f"  Total Header variables: {len(dxf_doc.header.varnames())}")
    print(f"  Total Layers: {len(dxf_doc.layers)}")
    print(f"  Total Blocks: {len(dxf_doc.blocks)}")
    print(f"  Total Modelspace: {len(list(dxf_doc.modelspace()))}")
    print(f"  Total Layouts: {len(dxf_doc.layouts) - 1}")  # Exclude modelspace
    print(f"  Total Viewports: {len(dxf_doc.viewports)}")
    print(f"  Total Classes: {class_count}")
    print(f"  Total Objects: {len(dxf_doc.objects)}")
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

    #path = "/Users/smg/Documents/Programming/Code/python/sampledxf/others/"
    path = "/Users/smg/Documents/Programming/Code/python/sampledxf/others/now4.dxf"

    process_path(path)
