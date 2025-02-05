from paddleocr import PaddleOCR
ocr = PaddleOCR()
result = ocr.ocr('Main_window.png',cls=False,bin=True)
print(result[0])#返回值：【【顶点列表】，（‘文字’，可信度）】
# det=True 且 rec=True:
# 返回一个列表，每个元素是对应图像的 OCR 结果。
# 每个 OCR 结果是一个列表，包含检测到的文本区域的边界框和识别出的文本。
#
# det=True 且 rec=False:
# 返回一个列表，每个元素是对应图像的检测到的文本边界框。
#
# det=False 且 rec=True:
# 返回一个列表，每个元素是对应图像的识别出的文本。
#
# det=False 且 rec=False:
# 返回一个列表，每个元素是对应图像的角度分类结果。