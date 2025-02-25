
import xml.etree.ElementTree as ET
import re


class XMLWebComponentConverter:
    """
    Utility class to convert XML to HTML web components.
    """
    # TODO check general design / implementation of the class
    # TODO check encoding ! must be utf-8
    # TODO clarify: class maps XML to HTML web components, but not complete HTML, only the web components - meant to be integrated as snippet in an already functional html!


    @staticmethod
    def xml_to_webcomponent(xml_string, web_component_prefix='my-'):
        """
        Universally transform any XML to HTML web components.

        Args:
            xml_string (str): The input XML string to transform
            web_component_prefix (str): The prefix to add to the web component tag names

        Returns:
            str: Transformed HTML snippet with web components
        """
        # Dictionary to hold namespace prefixes
        namespaces = {}

        def sanitize_tag(tag):
            """
            Convert XML tag to a valid web component tag name.
            - Remove any namespace if present
            - Convert to lowercase
            - Ensure it starts with a letter
            """
            # Remove namespace if present
            if '}' in tag:
                tag = tag.split('}')[-1]

            # Sanitize the tag name
            sanitized = re.sub(r'[^a-zA-Z0-9-]', '', tag).lower()

            # Ensure it starts with a letter
            if not re.match(r'^[a-zA-Z]', sanitized):
                sanitized = 'x-' + sanitized

            return f'{web_component_prefix}{sanitized}'

        def extract_namespaces(elem_string):
            """Extract namespace declarations from XML string"""
            import re
            ns_matches = re.findall(r'xmlns:([a-zA-Z0-9_-]+)="([^"]+)"', elem_string)
            for prefix, uri in ns_matches:
                namespaces[uri] = prefix

        def parse_namespaced_attr(attr):
            """Parse a namespaced attribute and return prefix:name format"""
            if '}' in attr:
                ns_uri, local_name = attr.split('}', 1)
                ns_uri = ns_uri[1:]  # Remove the leading '{'
                if ns_uri in namespaces:
                    return f"{namespaces[ns_uri]}:{local_name}"
            return attr

        def convert_element(element):
            """
            Recursively convert an XML element to a web component element
            """
            # Convert tag to sanitized web component format
            web_component_tag = sanitize_tag(element.tag)

            # Create attributes string
            attributes = []
            for key, value in element.attrib.items():
                attr_name = parse_namespaced_attr(key)
                attributes.append(f'{attr_name}="{str(value)}"')

            attr_str = ' '.join(attributes)
            opening_tag = f"<{web_component_tag} {attr_str}>" if attr_str else f"<{web_component_tag}>"

            # Process child elements and text content
            children = []

            # Add text content before first child
            if element.text and element.text.strip():
                children.append(element.text)

            # Process child elements
            for child in element:
                children.append(convert_element(child))

                # Add tail text after each child
                if child.tail and child.tail.strip():
                    children.append(child.tail)

            # Join children and create closing tag
            content = ''.join(children)
            return f"{opening_tag}{content}</{web_component_tag}>"

        # First, extract namespace declarations from the original XML string
        extract_namespaces(xml_string)

        # Add the known namespaces
        namespaces["http://www.w3.org/1999/02/22-rdf-syntax-ns#"] = "rdf"
        namespaces["http://www.tei-c.org/ns/1.0/"] = "tei"
        namespaces["http://www.opengis.net/ont/gml#"] = "lido"
        namespaces["http://purl.org/dc/elements/1.1/"] = "dc"

        # Register namespaces with ElementTree
        for uri, prefix in namespaces.items():
            ET.register_namespace(prefix, uri)

        # Parse the XML
        try:
            # Try parsing as XML string
            root = ET.fromstring(xml_string)
        except ET.ParseError:
            # If it fails, try parsing as XML file
            try:
                tree = ET.parse(xml_string)
                root = tree.getroot()
            except Exception as e:
                raise ValueError(f"Unable to parse XML: {e}")

        # Convert the root element and its children
        return convert_element(root)


# TODO remove test calls
# Comprehensive test function to demonstrate versatility
def test_xml_to_webcomponent():
    # Test cases covering various XML scenarios
    test_cases = [
        # Basic XML
        '''<root>Simple XML</root>''',

        # XML with attributes
        '''<person id="123" type="employee">John Doe</person>''',

        # Nested XML
        '''
        <company>
            <name>Acme Corp</name>
            <employees>
                <employee>John Doe</employee>
                <employee>Jane Smith</employee>
            </employees>
        </company>
        ''',

        # XML with special characters
        '''<data>Special chars: & < > " '</data>''',

        # XML with namespaces
        '''<ns:root xmlns:ns="http://example.com">Namespaced XML</ns:root>''',

        # Complex nested XML
        '''
        <library>
            <book isbn="1234567890">
                <title>Python Programming</title>
                <author>
                    <firstname>John</firstname>
                    <lastname>Doe</lastname>
                </author>
                <publication-year>2023</publication-year>
            </book>
        </library>
        '''
    ]

    # Test each XML input
    for idx, xml_input in enumerate(test_cases, 1):
        print(f"Test Case {idx}:")
        print("Input XML:")
        print(xml_input)
        print("\nConverted Web Components:")
        try:
            html_snippet = XMLWebComponentConverter.xml_to_webcomponent(xml_input, "memo-")
            print(html_snippet)
        except Exception as e:
            print(f"Error converting XML: {e}")
        print("\n" + "="*50 + "\n")

# Uncomment to run tests
# test_xml_to_webcomponent()