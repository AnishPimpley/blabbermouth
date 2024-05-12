from pydantic import BaseModel, Field
# random id generator 
import uuid

class BaseShape(BaseModel):
    """The schema describes a basic shape drawn on a whiteboard canvas"""
    id: str = Field(default='shape_' + str(uuid.uuid4())[:4])
    rotation: float = Field(default=0.0)
    opacity: float = Field(default=1.0)

class RectangleShape(BaseShape):
    """The schema describes a rectangle shape drawn on a whiteboard canvas"""
    x: float = Field(100.0, description="The x-coordinate of top-left corner of the shape")
    y: float = Field(100.0, description="The y-coordinate of top-left corner of the shape")
    width: float = Field(default=50.0)
    height: float = Field(default=50.0)
    fill_color: str = Field(default='blue')
    stroke_color: str = Field(default='black')
    stroke_width: float = Field(default=2.0)

class TextBoxShape(BaseShape):
    """The schema describes a text box shape drawn on a whiteboard canvas"""
    x: float = Field(100.0, description="The x-coordinate of the root of the text box")
    y: float = Field(100.0, description="The y-coordinate of the root of the text box")
    width: float = Field(default=200.0)
    height: float = Field(default=100.0)
    text: str = Field(default='Enter text here...', description="The content of the text box")
    font_size: int = Field(default=14)
    text_color: str = Field(default='black')
    background_color: str = Field(default='white')
    border_color: str = Field(default='black')
    border_width: float = Field(default=1.0)

class StickyNoteShape(BaseShape):
    """The schema describes a sticky note shape drawn on a whiteboard canvas"""
    x: float = Field(100.0, description="The x-coordinate of the root of the shape")
    y: float = Field(100.0, description="The y-coordinate of the root of the shape")
    width: float = Field(default=120.0)
    height: float = Field(default=120.0)
    text: str = Field(default='Note something...', description="The content of the sticky note")
    font_size: int = Field(default=12)
    note_color: str = Field(default='yellow')  # Typically a bright color like yellow

class ArrowShape(BaseModel):
    """The schema describes an arrow shape drawn on a whiteboard canvas."""
    start_x: float = Field(150.0, description="The x-coordinate of the starting point of the arrow")
    start_y: float = Field(150.0, description="The y-coordinate of the starting point of the arrow")
    end_x: float = Field(300.0, description="The x-coordinate of the ending point of the arrow")
    end_y: float = Field(150.0, description="The y-coordinate of the ending point of the arrow")
    stroke_color: str = Field(default='black')
    stroke_width: float = Field(default=3.0)
    opacity: float = Field(default=1.0)

class EllipseShape(BaseShape):
    """The schema describes an ellipse shape drawn on a whiteboard canvas"""
    center_x: float = Field(100.0, description="The x-coordinate of the root of center of the shape")
    center_y: float = Field(100.0, description="The y-coordinate of the root of center of the shape")
    radius_x: float = Field(default=50.0)
    radius_y: float = Field(default=50.0)
    fill_color: str = Field(default='blue')
    stroke_color: str = Field(default='black')
    stroke_width: float = Field(default=2.0)

class FunctionCallingConstants:

    SHAPES = {
        'rectangle': RectangleShape,
        'text_box': TextBoxShape,
        'sticky_note': StickyNoteShape,
        'arrow': ArrowShape,
        'ellipse': EllipseShape
    }

    SHAPE_ACTIONS = {
        'create': 'create',
        'update': 'update',
        'delete': 'delete',
        'move': 'move',
        'rotate': 'rotate',
    }

    