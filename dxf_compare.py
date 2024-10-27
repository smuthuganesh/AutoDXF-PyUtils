import os
import ezdxf

def compare_dxf_files(source_path, target_path):
    # Compare file sizes
    source_size = os.path.getsize(source_path)
    target_size = os.path.getsize(target_path)
    print(f"File Size - Source: {source_size} bytes, Target: {target_size} bytes")
    
    # Analyze and report on components contributing to the file size
    analyze_file_components(source_path, target_path)

    # Compare metadata
    source_metadata = get_dxf_metadata(source_path)
    target_metadata = get_dxf_metadata(target_path)

    print("\nMetadata Comparison:")
    for key in source_metadata.keys():
        source_value = source_metadata.get(key, "Not Found")
        target_value = target_metadata.get(key, "Not Found")
        print(f"{key}: Source - {source_value}, Target - {target_value}")

    # Compare internal entities
    source_entities = get_dxf_entities(source_path)
    target_entities = get_dxf_entities(target_path)

    print("\nEntities Count Comparison:")
    print(f"Source Entities: {len(source_entities)}, Target Entities: {len(target_entities)}")
    print(f"Entity Differences: {set(entity.dxftype() for entity in source_entities) - set(entity.dxftype() for entity in target_entities)}")

    # Compare entity properties
    compare_entity_properties(source_entities, target_entities)

    # Compare layer information
    compare_layers(source_path, target_path)

    # Compare block definitions
    compare_blocks(source_path, target_path)

    # Compare text content
    compare_text_content(source_entities, target_entities)

    # Compare unused styles
    compare_unused_styles(source_path, target_path)

def analyze_file_components(source_path, target_path):
    source_entities_count = count_entities(source_path)
    target_entities_count = count_entities(target_path)

    source_layers_count = count_layers(source_path)
    target_layers_count = count_layers(target_path)

    source_blocks_count = count_blocks(source_path)
    target_blocks_count = count_blocks(target_path)

    print("\nFile Component Analysis:")
    print(f"Source Entities Count: {source_entities_count}, Target Entities Count: {target_entities_count}")
    print(f"Source Layers Count: {source_layers_count}, Target Layers Count: {target_layers_count}")
    print(f"Source Blocks Count: {source_blocks_count}, Target Blocks Count: {target_blocks_count}")

def count_entities(filepath):
    try:
        dxf_doc = ezdxf.readfile(filepath)
        return len(list(dxf_doc.modelspace().query('*')))
    except Exception as e:
        print(f"Error counting entities in {filepath}: {e}")
        return 0

def count_layers(filepath):
    try:
        dxf_doc = ezdxf.readfile(filepath)
        return len(dxf_doc.layers)
    except Exception as e:
        print(f"Error counting layers in {filepath}: {e}")
        return 0

def count_blocks(filepath):
    try:
        dxf_doc = ezdxf.readfile(filepath)
        return len(dxf_doc.blocks)
    except Exception as e:
        print(f"Error counting blocks in {filepath}: {e}")
        return 0

def get_dxf_metadata(filepath):
    try:
        dxf_doc = ezdxf.readfile(filepath)
        metadata = {
            'version': dxf_doc.dxfversion,
            'author': dxf_doc.header.get('$AUTH', 'Not Specified'),
            'title': dxf_doc.header.get('$TITLE', 'Not Specified'),
            'created': dxf_doc.header.get('$TDCREATE', 'Not Specified'),
            'updated': dxf_doc.header.get('$TDUPDATE', 'Not Specified'),
        }
        return metadata
    except Exception as e:
        print(f"Error reading metadata from {filepath}: {e}")
        return {}

def get_dxf_entities(filepath):
    try:
        dxf_doc = ezdxf.readfile(filepath)
        return [entity for entity in dxf_doc.modelspace().query('*')]
    except Exception as e:
        print(f"Error reading entities from {filepath}: {e}")
        return []

def compare_entity_properties(source_entities, target_entities):
    source_entity_dict = {entity.dxf.handle: entity for entity in source_entities}
    target_entity_dict = {entity.dxf.handle: entity for entity in target_entities}

    print("\nEntity Properties Comparison:")
    for handle, source_entity in source_entity_dict.items():
        target_entity = target_entity_dict.get(handle)
        if target_entity:
            compare_entity_details(source_entity, target_entity)
        else:
            print(f"Entity {handle} only in source.")

    for handle in target_entity_dict:
        if handle not in source_entity_dict:
            print(f"Entity {handle} only in target.")

def compare_entity_details(source_entity, target_entity):
    if source_entity.dxftype() != target_entity.dxftype():
        print(f"Type mismatch for entity {source_entity.dxf.handle}: Source Type - {source_entity.dxftype()}, Target Type - {target_entity.dxftype()}")
        return

    differences = []
    for attr in ['color', 'layer', 'linetype', 'start', 'end', 'insert', 'text', 'contents']:
        source_value = getattr(source_entity.dxf, attr, "Not Specified")
        target_value = getattr(target_entity.dxf, attr, "Not Specified")
        if source_value != target_value:
            differences.append(f"{attr}: Source - {source_value}, Target - {target_value}")

    if differences:
        print(f"Differences for entity {source_entity.dxf.handle}: {', '.join(differences)}")

def compare_layers(source_path, target_path):
    source_layers = get_layers(source_path)
    target_layers = get_layers(target_path)

    print("\nLayer Comparison:")
    print(f"Source Layers: {source_layers}")
    print(f"Target Layers: {target_layers}")

def get_layers(filepath):
    try:
        dxf_doc = ezdxf.readfile(filepath)
        return [layer.dxf.name for layer in dxf_doc.layers]
    except Exception as e:
        print(f"Error reading layers from {filepath}: {e}")
        return []

def compare_blocks(source_path, target_path):
    source_blocks = get_blocks(source_path)
    target_blocks = get_blocks(target_path)

    print("\nBlock Comparison:")
    print(f"Source Blocks: {source_blocks}")
    print(f"Target Blocks: {target_blocks}")

def get_blocks(filepath):
    try:
        dxf_doc = ezdxf.readfile(filepath)
        return [block.name for block in dxf_doc.blocks]
    except Exception as e:
        print(f"Error reading blocks from {filepath}: {e}")
        return []

def compare_text_content(source_entities, target_entities):
    source_texts = {entity.dxf.handle: entity.dxf.text for entity in source_entities if entity.dxftype() in ['TEXT', 'MTEXT']}
    target_texts = {entity.dxf.handle: entity.dxf.text for entity in target_entities if entity.dxftype() in ['TEXT', 'MTEXT']}

    print("\nText Content Comparison:")
    for handle, source_text in source_texts.items():
        target_text = target_texts.get(handle)
        if target_text:
            if source_text != target_text:
                print(f"Text mismatch for entity {handle}: Source - {source_text}, Target - {target_text}")
        else:
            print(f"Text entity {handle} only in source.")

    for handle in target_texts:
        if handle not in source_texts:
            print(f"Text entity {handle} only in target.")

def compare_unused_styles(source_path, target_path):
    source_styles = get_styles(source_path)
    target_styles = get_styles(target_path)

    print("\nUnused Styles Comparison:")
    unused_in_source = set(source_styles) - set(target_styles)
    unused_in_target = set(target_styles) - set(source_styles)
    
    print(f"Unused Styles in Source: {unused_in_source}")
    print(f"Unused Styles in Target: {unused_in_target}")

def get_styles(filepath):
    try:
        dxf_doc = ezdxf.readfile(filepath)
        return [style.dxf.name for style in dxf_doc.styles]
    except Exception as e:
        print(f"Error reading styles from {filepath}: {e}")
        return []

if __name__ == "__main__":
    source_file = "/Users/smg/Documents/Programming/Code/python/sampledxf/others/now4.dxf"  # Replace with your source DXF file path
    target_file = "/Users/smg/Documents/Programming/Code/python/sampledxf/others/now4_out.dxf"  # Replace with your target DXF file path

    compare_dxf_files(source_file, target_file)
