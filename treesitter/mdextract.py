class MdExtract:

    def __init__(self) -> None:
        pass
    def read_file(self,filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.readlines()
    def splitter_function(self, src_path):
        lines = self.read_file(src_path)
        chunks = [lines[i:i + 20] for i in range(0, len(lines), 20)]
        datas_list = []
        for index, chunk in enumerate(chunks):
            chunk_text = ''.join(chunk)
            begin_byte = sum(len(line.encode('utf-8')) for line in lines[:index * 20])
            end_byte = begin_byte + len(chunk_text.encode('utf-8'))
            datas_list.append({
                'source_path': src_path,
                'begin_byte': begin_byte,
                'end_byte': end_byte,
                'name': f"chunk_{index}",
            })
        return datas_list