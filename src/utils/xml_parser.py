"""Module containing helper XML Parsing functions."""
import xml.etree.ElementTree as ET
from typing import Union


def parse_xml_to_dict(element: ET.Element) -> dict:
    """
    Recursively parse an XML element into a dictionary.

    Args:
    element (ET.Element): The XML element to parse.

    Returns:
    Dict[str, Any]: A dictionary representation of the XML element.
    """
    if not list(element):  # Base case: no child elements
        return parse_type(element.text)  # type: ignore

    return_dict = {}
    for child in element:
        child_dict = parse_xml_to_dict(child)
        if child.tag not in return_dict:
            return_dict[child.tag] = child_dict
        else:
            if not isinstance(return_dict[child.tag], list):
                # Convert to list if there are multiple children with the same tag
                return_dict[child.tag] = [return_dict[child.tag]]
            return_dict[child.tag].append(child_dict)

    return return_dict


def parse_xml_file(file_path: str) -> dict:
    """
    Parse an XML file and return a dictionary representation.

    Args:
    file_path (str): The file path to the XML file.

    Returns:
    Dict[str, Any]: A dictionary representation of the XML file.
    """
    xml_tree = ET.parse(file_path).getroot()
    return parse_xml_to_dict(xml_tree)


def is_float(text: str) -> bool:
    """
    Check if a given string represents a float.

    Args:
    text (str): The string to check.

    Returns:
    bool: True if the string can be converted to a float, False otherwise.
    """
    return text.replace(" ", "").replace(".", "").replace("-", "").isnumeric()


def parse_type(text: str) -> Union[str, float, bool, list, dict]:
    """
    Parse a string to its corresponding data type: float, boolean, list of floats, or string.

    Args:
    text (str): The string to parse.

    Returns:
    Union[str, float, bool, list]: The parsed data in its appropriate type.
    """
    if isinstance(text, str):
        if text.lower() == "true":
            return True

        if text.lower() == "false":
            return False

        if is_float(text):
            return float(text)

        if "," in text:
            vector = text.split(",")
            if all(is_float(n) for n in vector):
                return [float(n) for n in vector]
    return text


def print_keys_and_types(d, indent_level=0):
    """
    Recursively prints the keys and types of items in a nested dictionary or list of dictionaries.

    :param d: The dictionary or list of dictionaries to explore.
    :param indent_level: Current indentation level for pretty printing.
    """
    indent = "    " * indent_level
    if isinstance(d, dict):
        for key, value in d.items():
            print(f"{indent}{key}: {type(value).__name__}")
            if isinstance(value, (dict, list)):
                print_keys_and_types(value, indent_level + 1)
    elif isinstance(d, list):
        for index, item in enumerate(d):
            print(f"{indent}[{index}]: {type(item).__name__} - List Item")
            if isinstance(item, (dict, list)):
                print_keys_and_types(item, indent_level + 1)


def main() -> None:
    """test cases"""
    xml_file_path = "data/xml/Mobula.xml"
    parsed_xml = parse_xml_file(xml_file_path)
    print(parsed_xml)


if __name__ == "__main__":
    main()
