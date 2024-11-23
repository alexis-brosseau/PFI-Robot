import numpy as np
class Window:

    ORG_LEFT = (10,250)
    ORG_RIGHT = (10,300)
    RGB = (0,255,0)
    THICKNESS = 2
    LINE_TYPE = 2
    FONT_SCALE = 1
    RECTANGLE_BORDER = 3
    
    def __init__(self, cv2):
        self.cv2 = cv2
        self.screens = []
    
    def display(self):
        for screen in self.screens:
            self.cv2.imshow(screen[0], screen[1])

    def add_screen(self, title, frame):
        self.screens.append((title, frame))

    def __write(self, text, window, position):
        self.cv2.putText(window,
                        text,
                        position,
                        self.cv2.FONT_HERSHEY_SIMPLEX,
                        self.FONT_SCALE, 
                        self.RGB,
                        self.THICKNESS, 
                        self.LINE_TYPE)
        
    def draw_rectangle(self, frame, top_left, bottom_right, color):
        self.cv2.rectangle(frame, (int(top_left[0]), int(top_left[1])), (int(bottom_right[0]), int(bottom_right[1])), color, self.RECTANGLE_BORDER)
    
    def draw_circle(self, image, position, color):
        return self.cv2.circle(image, position, 1, color, -1)