import math
from collections import defaultdict
import ezdxf
from ezdxf import colors

def duplicate_dxf(source_path, target_path):
    source_doc = load_dxf(source_path)
    source_doc.layers.add(name="TESTLAYER", color=colors.RED)

    msp = source_doc.modelspace()
    if len(msp) == 0:
        print("No entities in modelspace to modify.")

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

def find_rectangles(dxf_doc):
    print("Finding all rectangle shapes in the DXF document.")
    rectangles = []
    
    # Helper function to get endpoint key with tolerance
    def get_endpoint_key(point, tolerance=1e-6):
        return (round(point[0]/tolerance)*tolerance, 
                round(point[1]/tolerance)*tolerance)
    
    # Helper function to calculate angle between two points
    def calculate_angle(p1, p2):
        return math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    
    # Create spatial index of line endpoints
    endpoint_to_lines = defaultdict(list)
    lines = [entity for entity in dxf_doc.modelspace() if entity.dxftype() == 'LINE']
    # Index all lines by their endpoints
    for line in lines:
        start = (line.dxf.start.x, line.dxf.start.y)
        end = (line.dxf.end.x, line.dxf.end.y)
        print(start, end)
        start_key = get_endpoint_key(start)
        end_key = get_endpoint_key(end)
        
        endpoint_to_lines[start_key].append((line, start, end))
        endpoint_to_lines[end_key].append((line, end, start))
    
    # Process each line as a potential rectangle side
    processed_sets = set()
    
    for line1 in lines:
        start1 = (line1.dxf.start.x, line1.dxf.start.y)
        end1 = (line1.dxf.end.x, line1.dxf.end.y)
        
        # Check connected lines at both endpoints
        for start_point, end_point in [(start1, end1), (end1, start1)]:
            start_key = get_endpoint_key(start_point)
            
            # Find perpendicular connected lines
            base_angle = calculate_angle(start_point, end_point)
            for connected_line, conn_start, conn_end in endpoint_to_lines[start_key]:
                if connected_line == line1:
                    continue
                    
                # Check if lines are perpendicular
                conn_angle = calculate_angle(conn_start, conn_end)
                angle_diff = abs((conn_angle - base_angle + math.pi/2) % math.pi)
                if abs(angle_diff - math.pi/2) > 0.01:  # Allow small tolerance
                    continue
                
                # Try to complete the rectangle
                conn_end_key = get_endpoint_key(conn_end)
                for third_line, third_start, third_end in endpoint_to_lines[conn_end_key]:
                    if third_line in {line1, connected_line}:
                        continue
                        
                    third_end_key = get_endpoint_key(third_end)
                    # Look for the fourth line
                    for fourth_line, fourth_start, fourth_end in endpoint_to_lines[third_end_key]:
                        if fourth_line in {line1, connected_line, third_line}:
                            continue
                            
                        # Check if it connects back to the first line
                        fourth_end_key = get_endpoint_key(fourth_end)
                        if fourth_end_key == get_endpoint_key(end_point):
                            # Found a rectangle! Check if we've seen it before
                            rect_set = frozenset([line1, connected_line, third_line, fourth_line])
                            if rect_set not in processed_sets:
                                rectangles.append([line1, connected_line, third_line, fourth_line])
                                processed_sets.add(rect_set)
    
    # Include closed LWPOLYLINE rectangles
    polylines = [entity for entity in dxf_doc.modelspace() if entity.dxftype() == 'LWPOLYLINE']
    for polyline in polylines:
        if len(polyline) == 4 and polyline.closed:
            rectangles.append(polyline)

    # Mark found rectangles
    for rect in rectangles:
        if isinstance(rect, list):  # Rectangles formed by LINE entities
            for line in rect:
                line.dxf.layer = "TESTLAYER"
        else:  # Rectangle from LWPOLYLINE entities
            rect.dxf.layer = "TESTLAYER"
            
    return rectangles  

if __name__ == "__main__":
    source_file = "/Users/smg/Documents/Programming/Code/python/sampledxf/kovai/Drawing1.dxf"  # Replace with your source DXF file path
    target_file = "/Users/smg/Documents/Programming/Code/python/sampledxf/kovai/Drawing1_out.dxf"  # Replace with your target DXF file path

    duplicate_dxf(source_file, target_file)
