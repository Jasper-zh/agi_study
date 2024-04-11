"""
rag_example - 从PDF读取文本内容

Author: zhang
Date: 2024/2/2
"""
from pdfminer.high_level import extract_pages # 提取每页
from pdfminer.layout import LTTextContainer   #


"""
filename: 文件地址
page_numbers: 取前几页
"""
def extract_text_from_pdf(filename, page_numbers=None, min_line_length=1):
    '''从 PDF 文件中（按指定页码）提取文字'''
    paragraphs = []
    buffer = ''
    full_text = ''
    # 遍历每页
    for i, page_layout in enumerate(extract_pages(filename)):
        # 如果指定了页码列表[1,4,5]，就只查看指定的页
        if page_numbers is not None and i not in page_numbers:
            continue
        # 遍历改页的元素
        for element in page_layout:
            # 如果元素是文本类型，则进行拼接
            if isinstance(element, LTTextContainer):
                full_text += element.get_text() + '\n'

    # 按空行分隔，获得文本列表
    lines = full_text.split('\n')
    for text in lines:
        # 忽略标题
        if len(text) >= min_line_length:
            # 将当前行拼接到缓冲区，如果此行结尾有'-'说明单词一部分被写到下行了，现在直接去掉
            buffer += (' '+text) if not text.endswith('-') else text.strip('-')
        elif buffer:
            paragraphs.append(buffer)
            buffer = ''
    if buffer:
        paragraphs.append(buffer)
    return paragraphs

if __name__ == '__main__':
    # 一行如果小于20可能是标题忽略掉
    paragraphs = extract_text_from_pdf("2402.17177.pdf", min_line_length=20)
    print(paragraphs)
    for para in paragraphs[0:10]:
        print(para + "\n")
