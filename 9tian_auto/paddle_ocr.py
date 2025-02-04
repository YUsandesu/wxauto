from paddleocr import PaddleOCR

ocr = PaddleOCR()
result = ocr.ocr('Main_window.png')
print(result)