import os
import sys
import zipfile
from xml.etree import ElementTree as ET


def process_svg_objects(svg_file, prefix):
    """
    Extracts individual SVG objects (e.g., <circle>, <rect>, <line>, etc.) from a given file.
    Returns a list of tuples containing the object index and the SVG string.
    """
    tree = ET.parse(svg_file)
    root = tree.getroot()

    # Identify SVG namespace
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    ET.register_namespace('', namespace['svg'])

    # Find all individual SVG elements
    object_tags = ['circle', 'rect', 'line', 'polygon', 'polyline', 'path', 'ellipse', 'text']
    objects = []
    for tag in object_tags:
        objects.extend(root.findall(f".//svg:{tag}", namespace))

    # Generate individual SVGs for each object
    object_svgs = []
    for idx, obj in enumerate(objects):
        # Create a new SVG with just this object
        object_svg = ET.Element(root.tag, root.attrib)
        object_svg.extend(root.findall("./svg:defs", namespace))  # Include <defs> if present
        object_svg.append(obj)

        # Convert the SVG element tree to a string
        object_content = ET.tostring(object_svg, encoding="unicode")
        object_svgs.append((f"{prefix}_{idx:04}.svg", object_content))

    return object_svgs


def create_zip(output_zip, foreground_path, background_path, collider_objects):
    """
    Creates a ZIP file containing the original foreground, background, and split collider objects.
    """
    with zipfile.ZipFile(output_zip, "w") as zipf:
        # Add foreground and background SVGs
        zipf.write(foreground_path, "foreground.svg")
        zipf.write(background_path, "background.svg")
        # Add collider objects
        for filename, content in collider_objects:
            zipf.writestr(filename, content)


def process_zip(input_zip, output_zip):
    """
    Processes the input ZIP file to extract foreground, background, and collider SVGs.
    Splits colliders into individual objects and compiles them into a new ZIP.
    """
    with zipfile.ZipFile(input_zip, "r") as zipf:
        # Extract the SVG files
        temp_dir = os.path.splitext(input_zip)[0] + "_temp"
        os.makedirs(temp_dir, exist_ok=True)
        zipf.extractall(temp_dir)

        # Paths to SVG files
        foreground_svg = os.path.join(temp_dir, "foreground.svg")
        background_svg = os.path.join(temp_dir, "background.svg")
        collider_svg = os.path.join(temp_dir, "collider.svg")

        # Validate files
        if not os.path.exists(foreground_svg) or not os.path.exists(background_svg) or not os.path.exists(collider_svg):
            print("Input ZIP must contain 'foreground.svg', 'background.svg', and 'collider.svg'.")
            return

        # Process collider objects
        collider_objects = process_svg_objects(collider_svg, "c")

        # Create the output ZIP
        create_zip(output_zip, foreground_svg, background_svg, collider_objects)

        # Clean up temporary files
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
        os.rmdir(temp_dir)

def main():
    # Get the input ZIP file from the command-line arguments
    if len(sys.argv) < 2:
        print("Usage: Drag and drop a ZIP file containing 'foreground.svg', 'background.svg', and 'collider.svg' onto the script.")
        return

    input_zip = sys.argv[1]
    if not os.path.exists(input_zip) or not input_zip.lower().endswith(".zip"):
        print("Please provide a valid ZIP file containing 'foreground.svg', 'background.svg', and 'collider.svg'.")
        return

    # Define the output ZIP file
    output_zip = "map.zip"

    # Process the input ZIP
    process_zip(input_zip, output_zip)


if __name__ == "__main__":
    main()