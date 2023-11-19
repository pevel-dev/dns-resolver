class QNameUtils:
    MAX_QNAME_LENGTH = 256

    def __init__(self):
        self.pointers = dict()

    def pack(self, name: str, current_offset: int) -> tuple[bytes, int]:
        data = []
        current_name = name
        while True:
            save_name = current_name
            save_offset = current_offset

            if pointer := self.pointers.get(current_name):
                pointer |= 0xC000
                pointer = int.to_bytes(pointer, 2, 'big')
                current_offset += 2
                data.append(pointer)
                break
            else:
                new_string = current_name.split('.', 1)
                length = int.to_bytes(len(new_string[0]), 1, 'big')
                data.append(length)
                current_offset += 1
                for i in new_string[0]:
                    data.append(i.encode(encoding='ascii'))
                    current_offset += 1
                if len(new_string) == 1:
                    self.pointers[save_name] = save_offset
                    data.append(b'\x00')
                    current_offset += 1
                    break
                current_name = new_string[1]
            self.pointers[save_name] = save_offset

        return b''.join(data), current_offset

    def parse(self, data: bytes, offset: int) -> tuple[str, int]:
        pointer = offset
        length = 0
        current_length = 0
        result = []
        while data[pointer] != 0x00:
            if length == 0 or length == current_length:
                if length != 0:
                    result.append('.')
                if data[pointer] & 0xc0 == 0xc0:
                    compress_pointer = (data[pointer] & 0x3F) + data[pointer + 1]
                    additional_string, _ = self.parse(data, compress_pointer)
                    result.append(additional_string)
                    pointer += 1
                    break

                length = data[pointer]
                current_length = 0
            else:
                current_length += 1
                result.append(chr(data[pointer]))
            pointer += 1

            if pointer - offset > self.MAX_QNAME_LENGTH:
                return None, 0
        pointer += 1

        return ''.join(result), pointer
