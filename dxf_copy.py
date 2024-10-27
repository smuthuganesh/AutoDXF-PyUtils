import ezdxf

def duplicate_dxf(source_path, target_path):
    source_doc = load_dxf(source_path)
    source_doc.saveas(target_path)
    print(f"Exact copy created at: {target_path}")


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

if __name__ == "__main__":
    source_file = "/Users/smg/Documents/Programming/Code/python/sampledxf/others/now4.dxf"  # Replace with your source DXF file path
    target_file = "/Users/smg/Documents/Programming/Code/python/sampledxf/others/now4_out.dxf"  # Replace with your target DXF file path

    duplicate_dxf(source_file, target_file)
