import json
import sys

# import bencodepy - available if you need it!
# import requests - available if you need it!

def list_maker(bencoded_elements):
    element_list, bencoded_elements = [], bencoded_elements[1:-1]
    while bencoded_elements:
        current_element, bencoded_length = decode_bencode(bencoded_elements)
        element_list.append(current_element)
        bencoded_elements = bencoded_elements[bencoded_length:]
    return element_list

def byte_cleaner(*elements):
     # bytes to string has the format b'<whatever>', so we have to take the b and the apostrophes out
    cleaned = []
    for e in elements:
        if isinstance(e, bytes): cleaned.append(str(e)[2:-1])
        else: cleaned.append(e)
    return tuple(cleaned)

def decode_bencode(bencoded_value):
    match (delimiter:=chr(bencoded_value[0])):
        case str() if delimiter.isdigit():
            first_colon_index = bencoded_value.find(b":")
            if first_colon_index == -1:
                raise ValueError("Invalid encoded value")
            encoded_string_length = int(bencoded_value[:first_colon_index])
            start, end = first_colon_index + 1, encoded_string_length + first_colon_index + 1
            return bencoded_value[start:end], end

        case 'i':
            start, end = 1, bencoded_value.find(b"e")
            return int(bencoded_value[start:end]), end + 1

        case 'l':
            return list_maker(bencoded_value), 0

        case 'd':
            element_dictionary, element_list = {}, list_maker(bencoded_value)
            i = 0
            while i < len(element_list):
                key, value = byte_cleaner(element_list[i], element_list[i+1])
                element_dictionary[key] = value
                i += 2
            return element_dictionary, 0

        case _:
            raise NotImplementedError("nuh uh")

def main():
    command = sys.argv[1]

    if command == "decode":
        bencoded_value = sys.argv[2].encode()

        # json.dumps() can't handle bytes, but bencoded "strings" need to be
        # bytestrings since they might contain non utf-8 characters.
        #
        # Let's convert them to strings for printing to the console.
        def bytes_to_str(data):
            if isinstance(data, bytes):
                return data.decode()

            raise TypeError(f"Type not serializable: {type(data)}")

        # Uncomment this block to pass the first stage
        print(json.dumps(decode_bencode(bencoded_value)[0], default=bytes_to_str))
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
