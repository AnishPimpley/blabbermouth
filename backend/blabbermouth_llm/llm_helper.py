import os
from groq import Groq
import sys
sys.path.append("/home/anish_2204/repos/blabbermouth")

from dotenv import load_dotenv
from inspect import cleandoc
load_dotenv()

from pydantic import BaseModel, Field
from backend.blabbermouth_llm.base_models import RectangleShape, StickyNoteShape, ArrowShape, TextBoxShape, FunctionCallingConstants, EllipseShape
from pprint import pprint
import io
import json
import uuid
class FeedbackAndFixInstructions(BaseModel):
    """ Instructions for providing feedback and fixing the tasks. In cases where no fixes are needed, then put the tasks into final_list_of_tasks as is, then it means no changes are needed. """
    feedback : list = Field([], description= "Feedbacks for the on problems in the tasks that would lead to an ugly layout.")
    fixes : list = Field([], description="The suggested fixes based on the feedbacks.")
    final_list_of_tasks : list[str] = Field(..., description="The tasks after fixing them. If no changes are needed, then copy the tasks into a list of strings as is.")


def raw_tasks_from_transcipt(transcript: str, current_white_board_state: list, cursor_position: tuple[float,float]):
    client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
    )

    # Create a StringIO object
    current_white_board_state_repr = io.StringIO()

    # Redirect the output of pprint to the StringIO object
    pprint(current_white_board_state, stream=current_white_board_state_repr)
    # Get the output as a string
    current_white_board_state_repr = current_white_board_state_repr.getvalue()

    # Print the output
    print(current_white_board_state_repr)

    list_tasks_prompt = [
        {
        "role": "system",
        "content": cleandoc(f"""
            You are a unit task enumerator for an AI whiteboard. Given the voice transcript of a user, you have to concretely verbalize all of the unit tasks that have been expressed in the user's voice transcript. 

            ### Broad types of tasks that can be performed on an AI whiteboard:
            * The possible shapes are as follows: {list(FunctionCallingConstants.SHAPES.keys()).__repr__()}
            * The possible actions are as follows: {list(FunctionCallingConstants.SHAPE_ACTIONS.keys()).__repr__()}

                            
            ### What is a unit task?
            A unit task is a single, atomic task that can be performed by the AI. It is the smallest unit of work that can be performed by the AI. For example, if the user says "Please add a new task to my to-do list", then the unit task is "add a new task to my to-do list".
            An example of a complex task is "Please add a new task to my to-do list and send me a notification when it is due". In this case, there are two unit tasks: "add a new task to my to-do list" and "send me a notification when it is due".

            ### Instructions for how to enumerate unit tasks:
            1. Only identify the unit tasks that can be performed on an AI whiteboard.         
            2. Be detailed. The goal isn't to create the perfect function call just yet. The goal is to identify all the unit tasks that can be performed on an AI whiteboard.
            3. Identify the tasks in the order that they must be performed   
            4. If a task needs to be broken down into smaller tasks, then break it down into smaller tasks. 
            5. Ignore random words, filler words, and any other irrelevant information.
            6. Nest the tasks for each instance of a shape
            7. User might be pointing to the shapes while speaking. You will be given the cursor location of the user. If the user transcripts indicates they want to put it in a specific location, then you should verbaliize that as well.                
            Output the unit tasks in a markdown list format . All the tasks for a single shape should be in 1 list item.
            8. Contextualize the tasks you identify within the existing whiteboard.                 
            9. The cursor doesn't always matter. If the task is fairly obvious, you can ignore the cursor location.
            """),
        },
        {
            "role": "user",
            "content": cleandoc(f"""
                The existing whiteboard is as follows:
                ```current_white_board_state
                {current_white_board_state_repr}
                ```

                Enumerate the unit tasks that can be performed on an AI whiteboard based on the following user transcript:     
                User cursor location: {cursor_position.__repr__()}
                User transcript:    
                ```
                {transcript}            
                ```
                Before writing the unit tasks, think out loud about the problem.

                Here are the unit tasks that can be performed on an AI whiteboard:
                *
                """)
            }
        ]
    
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=list_tasks_prompt)

    raw_tasks = response.choices[0].message.content

    print(raw_tasks)
    return raw_tasks

def get_fixed_tasks_from_raw_tasks(raw_tasks: str):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
        )

    list_tasks_prompt = [
        {
        "role": "system",
        "content": cleandoc(f"""
            You are a discerning checker and fixer for an AI whiteboard. Given a set of drawing tasks, you have to verify if tasks make sense from a visual perspective. 
            Based on your expertise, edit the tasks to make them visually appealing.
            
            ### Some examples of what makes for a visually appealing layout?
            * The layout should avoid ugly overlaps
            * Space the shapes out evenly to make the layout look clean
            * Avoid cluttering the shapes together, use the open space on the whiteboard effectively (it is a 1000x1000 whiteboard
            * Make sure the text is readable and not too small
            * If one task obscures another tasks, fix opacity or move the shape to make it visually appealing.
                            

            ### Instructions for how to provide feedbacks and fix the tasks:
            1. If there is ambiguity in any of the tasks, your job is to make them clear. You can make assumptions as needed.
            2. If the suggested tasks would lead to an ugly layout, then change the tasks to make the layout visually appealing.
            3. If you suspect some ugly overlap, then make sure to fix that as well.
            4. If no changes are needed, then copy the tasks into the fixed_nested_markdown_list as is.
            
            First run the sanity check on the tasks and then make the necessary edits to make the tasks visually appealing.
                            
            The output should be in json format. 
                            
            The JSON object must use the schema: {json.dumps(FeedbackAndFixInstructions.model_json_schema(), indent=2)}"
            """),
        },
        {
            "role": "user",
            "content": cleandoc(f"""
                Provide feedbacks and fix the raw tasks based on those feedbacks.
                                
                raw tasks that might need to be fixed:    
                ```
                {raw_tasks}            
                ```
                The feedbacks and fixes in json format are as follows:
                """)
        }
    ]


    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=list_tasks_prompt,
        response_format={"type": "json_object"},
        )

    fixed_tasks_json = response.choices[0].message.content

    feedback_and_fixes = FeedbackAndFixInstructions(**json.loads(fixed_tasks_json))
    return feedback_and_fixes

def get_tkinter_whiteboard_code_from_transcript(fixed_list_of_tasks: str):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
        )

    fixed_list_of_tasks_repr = "\n".join(fixed_list_of_tasks)

    tkinter_function_prompt = cleandoc(f"""
        Create a create_window() tkinter function that will perform the tasks of drawing the right shapes on the whiteboard.

        Note:
        1. The whiteboard is 1000x1000 pixels.
        2. The shapes should be drawn in the order they are listed in the tasks.

        The tkinter create_window() function will be called through a main function like so:
        ```python
        if __name__ == "__main__":
        create_window()               
        ```

        The state of the whiteboard at the start:
        ```python
        empty
        ```
        The list of tasks that need to be performed:
        ```markdown
        {fixed_list_of_tasks_repr}
        ```
        The self-contained create_window tkinter function that will draw the shapes on the whiteboard:
        ```python
        """)

    messages = [
        {
            "role": "user",
            "content": tkinter_function_prompt
        }
    ]

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages)

    tkinter_code = response.choices[0].message.content

    # find the code within ```python``` and execute it
    try:
        tkinter_code = tkinter_code.split("```python")[1].split("```")[0]
    except:
        tkinter_code = tkinter_code.split("```Python")[1].split("```")[0]

    print(tkinter_code)
    return tkinter_code

def get_tasks_from_transcript(transcript: str, current_white_board_state: list, cursor_position: tuple[float, float]):
    raw_tasks = raw_tasks_from_transcipt(transcript, current_white_board_state, cursor_position)
    #feedback_and_fixes = get_fixed_tasks_from_raw_tasks(raw_tasks)
    #fixed_list_of_tasks = feedback_and_fixes.final_list_of_tasks
    return raw_tasks


def update_whiteboard_state_by_tasks(tasks: str, current_white_board_state: list, cursor_position: tuple[float, float]):
    map_shape_and_action_prompt = f"""
        You are a whiteboard assistant. You have been given a list of tasks to perform on a whiteboard. 
        Each task is an action on an existing/new shape that updates the state of the white board. 
        You have to perform the actions on the shape and reach the final intended whiteboard state. 

        __________________________________________________________

        The possible shapes are as follows: {list(FunctionCallingConstants.SHAPES.keys()).__repr__()}

        The possible actions are as follows: {list(FunctionCallingConstants.SHAPE_ACTIONS.keys()).__repr__()}

        __________________________________________________________

        The pydantic schemas that represent the shapes are as follows:

        class BaseShape(BaseModel):
            \"""The schema describes a basic shape drawn on a whiteboard canvas\"""
            id: str = Field(default='shape_' + str(uuid.uuid4())[:4])
            rotation: float = Field(default=0.0)
            opacity: float = Field(default=1.0)

        class RectangleShape(BaseShape):
            \"""The schema describes a rectangle shape drawn on a whiteboard canvas\"""
            x: float = Field(100.0, description="The x-coordinate of top-left corner of the shape")
            y: float = Field(100.0, description="The y-coordinate of top-left corner of the shape")
            width: float = Field(default=50.0)
            height: float = Field(default=50.0)
            fill_color: str = Field(default='blue')
            stroke_color: str = Field(default='black')
            stroke_width: float = Field(default=2.0)

        class TextBoxShape(BaseShape):
            "The schema describes a text box shape drawn on a whiteboard canvas"
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
            "The schema describes a sticky note shape drawn on a whiteboard canvas"
            x: float = Field(100.0, description="The x-coordinate of the root of the shape")
            y: float = Field(100.0, description="The y-coordinate of the root of the shape")
            width: float = Field(default=120.0)
            height: float = Field(default=120.0)
            text: str = Field(default='Note something...', description="The content of the sticky note")
            font_size: int = Field(default=12)
            note_color: str = Field(default='yellow')  # Typically a bright color like yellow

        class ArrowShape(BaseModel):
            "The schema describes an arrow shape drawn on a whiteboard canvas."
            start_x: float = Field(150.0, description="The x-coordinate of the starting point of the arrow")
            start_y: float = Field(150.0, description="The y-coordinate of the starting point of the arrow")
            end_x: float = Field(300.0, description="The x-coordinate of the ending point of the arrow")
            end_y: float = Field(150.0, description="The y-coordinate of the ending point of the arrow")
            stroke_color: str = Field(default='black')
            stroke_width: float = Field(default=3.0)
            opacity: float = Field(default=1.0)

        class EllipseShape(BaseShape):
            "The schema describes an ellipse shape drawn on a whiteboard canvas"
            center_x: float = Field(100.0, description="The x-coordinate of the root of center of the shape")
            center_y: float = Field(100.0, description="The y-coordinate of the root of center of the shape")
            radius_x: float = Field(default=50.0)
            radius_y: float = Field(default=50.0)
            fill_color: str = Field(default='blue')
            stroke_color: str = Field(default='black')
            stroke_width: float = Field(default=2.0)

        __________________________________________________________

        __________________________________________________________

        The current state of the whiteboard is as follows: 
        ``` python
        # current_white_board_state: list = {current_white_board_state.__repr__()}
        # assume that current_white_board_state is a list of shapes drawn on the whiteboard. assume it is a variable that is already defined in the code.
        ```
        __________________________________________________________

        The whiteboard tasks are as follows: {tasks}

        __________________________________________________________
        ### Instructions:
        * If a task if redundant or unnecessary, ignore it.
        * please write the python code inside one ```python``` code block.
        * the current cursor position is {cursor_position.__repr__()}
        # assume the current_white_board_state variable is already defined 
        * explicitly make sure to update the current_white_board_state variable with the new state of the whiteboard.
        __________________________________________________________

        Use python to do the tasks and edit the state of the whiteboard.

        we will run exec(output_code) to get the final state of the whiteboard.

        __________________________________________________________

        Output code:
        """

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "user", "content": map_shape_and_action_prompt},
        ]
    )

    output_python  = response.choices[0].message.content
    output_python = output_python.strip()
    if "```python" in output_python:
        output_python = output_python.split("```python")[1].split("```")[0]
    elif "```Python" in output_python:
        output_python = output_python.split("```Python")[1].split("```")[0]
    elif "```\npython" in output_python:
        output_python = output_python.split("```\npython")[1].split("```")[0]
    elif "```\nPython" in output_python:
        output_python = output_python.split("```\nPython")[1].split("```")[0]
    else:
        Exception("Code block not found in the output")
    output_python = output_python.strip()
    
    print("output python code:\n\n", output_python)
    try:
        exec(output_python)
    except Exception as e:
        print("Error in executing the code: ", e)
        
    return current_white_board_state