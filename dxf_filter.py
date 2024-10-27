import math
import ezdxf
from ezdxf import colors

def duplicate_dxf(source_path, target_path):
    source_doc = load_dxf(source_path)
    source_doc.layers.add(name="TESTLAYER", color=colors.RED)

    find_rectangles(source_doc)

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


def is_perpendicular(line1, line2):
    """Check if two lines are perpendicular by comparing their direction vectors."""
    vec1 = (line1.dxf.end.x - line1.dxf.start.x, line1.dxf.end.y - line1.dxf.start.y)
    vec2 = (line2.dxf.end.x - line2.dxf.start.x, line2.dxf.end.y - line2.dxf.start.y)
    dot_product = vec1[0] * vec2[0] + vec1[1] * vec2[1]
    return abs(dot_product) < 1e-6

def find_rectangles(dxf_doc):
    print("Finding all rectangle shapes in the DXF document.")
    rectangles = []
    
    # Collect all LINE entities in the modelspace
    lines = [entity for entity in dxf_doc.modelspace() if entity.dxftype() == 'LINE']
    
    # Check pairs of lines to find potential rectangles
    for i, line1 in enumerate(lines):
        for j, line2 in enumerate(lines):
            if i >= j:
                continue  # Skip duplicate and same-line pairs
            if not is_perpendicular(line1, line2):
                continue  # Only consider perpendicular lines

            # Search for two additional lines that connect to line1 and line2 to form a rectangle
            potential_rectangle = [line1, line2]
            endpoints = {(line1.dxf.start.x, line1.dxf.start.y), (line1.dxf.end.x, line1.dxf.end.y),
                         (line2.dxf.start.x, line2.dxf.start.y), (line2.dxf.end.x, line2.dxf.end.y)}

            for line3 in lines:
                if line3 in potential_rectangle:
                    continue
                if len(endpoints & {(line3.dxf.start.x, line3.dxf.start.y), (line3.dxf.end.x, line3.dxf.end.y)}) == 1:
                    if is_perpendicular(line2, line3):
                        potential_rectangle.append(line3)
                        endpoints.update([(line3.dxf.start.x, line3.dxf.start.y), (line3.dxf.end.x, line3.dxf.end.y)])
            
            # Check if four lines form a closed loop with four unique corners
            if len(potential_rectangle) == 4 and len(endpoints) == 4:
                rectangles.append(potential_rectangle)
                
    # Include closed LWPOLYLINE rectangles
    polylines = [entity for entity in dxf_doc.modelspace() if entity.dxftype() == 'LWPOLYLINE']
    for polyline in polylines:
        if len(polyline) == 4 and polyline.closed:
            rectangles.append(polyline)

    for rect in rectangles:
        if isinstance(rect, list):  # Rectangles formed by LINE entities
            for line in rect:
                line.dxf.layer = "TESTLAYER"
        else:  # Rectangle from LWPOLYLINE entities
            rect.dxf.layer = "TESTLAYER"


if __name__ == "__main__":
    source_file = "/Users/smg/Documents/Programming/Code/python/sampledxf/others/now4.dxf"  # Replace with your source DXF file path
    target_file = "/Users/smg/Documents/Programming/Code/python/sampledxf/others/now4_out.dxf"  # Replace with your target DXF file path

    duplicate_dxf(source_file, target_file)
