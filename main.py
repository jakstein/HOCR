import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint, QRect, QTimer
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
import mss
import mss.tools

# azure stuff
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient

# insert ur Azure credentials here TODO: maybe use env or config file
AZURE_VISION_ENDPOINT = ""
AZURE_VISION_KEY = ""
AZURE_TRANSLATOR_ENDPOINT = ""
AZURE_TRANSLATOR_KEY = ""
AZURE_TRANSLATOR_REGION = ""
SOURCE_LANGUAGE = ""
# Azure credentials end

class TextDisplayWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags( # flags
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(400, 100, 300, 150)
        self.textContent = "Right-click the selection box to translate, middle-click/esc to close."
        self.fontSize = 12
        self.textColor = QColor(255, 255, 255, 255)        
    def setText(self, text):
        self.textContent = text
        self.update()  
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        font = QFont()
        font.setPointSize(self.fontSize)
        font.setBold(True)
        painter.setFont(font)
        
        textRect = self.rect().adjusted(10, 10, -10, -10)
        
        # Draw black outline by drawing text multiple times with slight offsets (copilot implementation of outlines)
        outlineColor = QColor(0, 0, 0, 255)  # Solid black outline
        painter.setPen(QPen(outlineColor, 2))  # 2px thick outline
        
        # Draw outline in 8 directions
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dx, dy in offsets:
            outlineRect = textRect.adjusted(dx, dy, dx, dy)
            painter.drawText(outlineRect, Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap, self.textContent)
        
        # Draw main white text on top
        painter.setPen(self.textColor)
        painter.drawText(textRect, Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap, self.textContent)        
    def moveToPosition(self, x, y):
        self.move(x, y)

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 300, 150)

        self.oldPos = QPoint()
        self.isResizing = False
        self.resizeMargin = 10

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.borderColor = QColor(0, 255, 0, 150)
        
        # showing the configured text display widget
        self.textDisplay = TextDisplayWidget()
        self.textDisplay.show()
        
        # make the text follow the overlay
        self.updateTextPosition()        
        # setting up azure clients
        try:
            self.translationClient = TextTranslationClient(
                endpoint=AZURE_TRANSLATOR_ENDPOINT,
                credential=AzureKeyCredential(AZURE_TRANSLATOR_KEY),
                region=AZURE_TRANSLATOR_REGION
            )
        except Exception as e:
            print(f"Error initializing Azure Translator: {e}")
            self.translationClient = None
        
        try:
            self.visionClient = ImageAnalysisClient(
                endpoint=AZURE_VISION_ENDPOINT,
                credential=AzureKeyCredential(AZURE_VISION_KEY)
            )
        except Exception as e:
            print(f"Error initializing Azure Vision: {e}")
            self.visionClient = None

    def updateTextPosition(self):
        # make the text display appear to the right of the overlay
        overlayGeom = self.geometry()
        textX = overlayGeom.x() + overlayGeom.width() + 20  # 20px gap        
        textY = overlayGeom.y()
        self.textDisplay.moveToPosition(textX, textY)
        self.textDisplay.resize(300, overlayGeom.height())

    def moveEvent(self, event):
        # update text position when overlay moves
        super().moveEvent(event)
        self.updateTextPosition()
        
    def resizeEvent(self, event):
        # make the text also resize when the overlay resizes
        super().resizeEvent(event)
        self.updateTextPosition()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # the semi transparent filling thing for overlay, you can disable it if you want (it's handy cause you can drag with it)
        painter.fillRect(self.rect(), QColor(100, 100, 100, 30)) 
          # the green border
        pen = QPen(self.borderColor, 8) # 8px thick border, can change the thickness here
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1)) # draw inside

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            # right click for capturing ocr and translation
            self.captureAndProcess()
        elif event.button() == Qt.MouseButton.MiddleButton:
            # middle click for closing the app 
            QApplication.quit()
        elif event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()
            # resizing logic (copilot assisted)
            rect = self.rect()
            if (abs(event.position().x() - rect.right()) < self.resizeMargin and
                abs(event.position().y() - rect.bottom()) < self.resizeMargin):
                self.isResizing = True
                self.resizeEdge = "bottom_right"
            else:
                self.isResizing = False
            if (abs(event.position().x() - rect.right()) < self.resizeMargin and
                abs(event.position().y() - rect.bottom()) < self.resizeMargin):
                self.isResizing = True
                self.resizeEdge = "bottom_right"
            else:
                self.isResizing = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.oldPos
            if self.isResizing and self.resizeEdge == "bottom_right":
                newWidth = self.width() + delta.x()
                newHeight = self.height() + delta.y()
                if newWidth > 50 and newHeight > 50: # minimum size (don't go below 50x50 cause that's azure's minimum size)
                    self.resize(newWidth, newHeight)
            elif not self.isResizing:
                self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.isResizing = False

    def captureAndProcess(self):
        if not self.visionClient or not self.translationClient:
            self.textDisplay.setText("Azure services not configured. Check credentials.")
            print("Azure services not configured. OCR/Translation aborted.")
            return

        geom = self.geometry()
        captureArea = {'top': geom.y(), 'left': geom.x(), 
                        'width': geom.width(), 'height': geom.height()}

        try:
            with mss.mss() as sct:
                sctImg = sct.grab(captureArea)
                imgBytes = mss.tools.to_png(sctImg.rgb, sctImg.size)

            # ocr bit
            japaneseText = self.performOcr(imgBytes)
            print(f"OCR Result: {japaneseText}")
            self.textDisplay.setText(f"OCR: {japaneseText}\nTranslating...")

            # ttranslation bit
            if japaneseText:
                englishText = self.performTranslation(japaneseText)
                print(f"Translation: {englishText}")
            else:
                englishText = "No text found by OCR."     
            # display result in floating text box
            self.textDisplay.setText(englishText)

        except Exception as e:
            errorMessage = f"Error during capture/proces: {e}"
            print(errorMessage)
            self.textDisplay.setText(errorMessage)

    def performOcr(self, imageDataBytes):
        if not self.visionClient:
            return "OCR client not initialized."
        try:
            result = self.visionClient.analyze(
                image_data=imageDataBytes,
                visual_features=[VisualFeatures.READ] # use the read feature for ocr
            )
            
            textLines = []
            if result.read is not None:
                for block in result.read.blocks:
                    for line in block.lines:
                        textLines.append(line.text)
            
            return " ".join(textLines) if textLines else "No text detected by Azure Vision."
        except Exception as e:
            print(f"Azure Vision OCR error: {e}")
            return f"OCR Error: {e}"

    def performTranslation(self, japaneseText):
        if not self.translationClient:
            return "Translator client not initialized."
        if not japaneseText.strip():
            return "No text to translate."
        try:
            response = self.translationClient.translate(
                body=[{'text': japaneseText}],
                to_language=['en'],
                from_language=SOURCE_LANGUAGE # TODO: use autodetect for multi language support
            )
            if response and response[0].translations:
                return response[0].translations[0].text
            return "Translation failed or no result."
        except Exception as e:
            print(f"Azure Translator error: {e}")
            return f"Translation Error: {e}"

    def closeEvent(self, event):
        # ensure text is closed when overlay is closed
        if hasattr(self, 'textDisplay'):
            self.textDisplay.close()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    overlay = OverlayWindow()
    
    overlay.show()
    
    sys.exit(app.exec())