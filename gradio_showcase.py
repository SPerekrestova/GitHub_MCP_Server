#!/usr/bin/env python3
"""
Gradio Comprehensive Showcase
=============================

This file demonstrates all major Gradio features and components.
Each section contains executable examples showcasing different functionality.

Run with: python gradio_showcase.py
Then open http://localhost:7860 in your browser.

Requirements:
    pip install gradio>=4.0.0 numpy pandas matplotlib pillow

"""

import gradio as gr
import numpy as np
import pandas as pd
import time
import json
import random
from datetime import datetime
from typing import List, Tuple, Optional

# ============================================================================
# SECTION 1: BASIC INTERFACE
# ============================================================================

def basic_interface_example():
    """
    Basic gr.Interface - The simplest way to create a Gradio app.
    Interface wraps a function with inputs and outputs automatically.
    """

    def greet(name: str) -> str:
        return f"Hello, {name}! Welcome to Gradio."

    demo = gr.Interface(
        fn=greet,
        inputs=gr.Textbox(label="Your Name", placeholder="Enter your name..."),
        outputs=gr.Textbox(label="Greeting"),
        title="Basic Interface Example",
        description="A simple greeting function demonstrating gr.Interface",
        examples=[["Alice"], ["Bob"], ["Charlie"]],
        theme="soft"
    )
    return demo


# ============================================================================
# SECTION 2: INPUT COMPONENTS
# ============================================================================

def input_components_showcase():
    """
    Showcase all major input components available in Gradio.
    """

    def process_all_inputs(
        text: str,
        number: float,
        slider: int,
        checkbox: bool,
        checkboxgroup: List[str],
        radio: str,
        dropdown: str,
        multiselect: List[str],
        color: str,
        datetime_val: str,
        code: str
    ) -> str:
        result = f"""
## Input Values Received:

| Component | Value |
|-----------|-------|
| Textbox | {text} |
| Number | {number} |
| Slider | {slider} |
| Checkbox | {checkbox} |
| CheckboxGroup | {checkboxgroup} |
| Radio | {radio} |
| Dropdown | {dropdown} |
| MultiSelect | {multiselect} |
| ColorPicker | {color} |
| DateTime | {datetime_val} |
| Code Length | {len(code)} chars |
"""
        return result

    with gr.Blocks(title="Input Components Showcase") as demo:
        gr.Markdown("# Input Components Showcase")
        gr.Markdown("Demonstrating all major input components in Gradio")

        with gr.Row():
            with gr.Column():
                # Text Input
                text_input = gr.Textbox(
                    label="Textbox",
                    placeholder="Enter some text...",
                    lines=2,
                    max_lines=5,
                    info="A basic text input field"
                )

                # Number Input
                number_input = gr.Number(
                    label="Number",
                    value=42,
                    minimum=0,
                    maximum=100,
                    step=0.5,
                    info="Numeric input with min/max constraints"
                )

                # Slider
                slider_input = gr.Slider(
                    label="Slider",
                    minimum=0,
                    maximum=100,
                    value=50,
                    step=1,
                    info="Drag to select a value"
                )

                # Checkbox
                checkbox_input = gr.Checkbox(
                    label="Single Checkbox",
                    value=True,
                    info="Toggle on/off"
                )

                # Checkbox Group
                checkboxgroup_input = gr.CheckboxGroup(
                    choices=["Option A", "Option B", "Option C", "Option D"],
                    label="Checkbox Group",
                    value=["Option A"],
                    info="Select multiple options"
                )

            with gr.Column():
                # Radio Buttons
                radio_input = gr.Radio(
                    choices=["Small", "Medium", "Large", "Extra Large"],
                    label="Radio Buttons",
                    value="Medium",
                    info="Select one option"
                )

                # Dropdown (Single Select)
                dropdown_input = gr.Dropdown(
                    choices=["Python", "JavaScript", "Rust", "Go", "TypeScript"],
                    label="Dropdown (Single)",
                    value="Python",
                    info="Select from dropdown"
                )

                # Dropdown (Multi Select)
                multiselect_input = gr.Dropdown(
                    choices=["Red", "Green", "Blue", "Yellow", "Purple"],
                    label="Dropdown (Multi-Select)",
                    value=["Red", "Blue"],
                    multiselect=True,
                    info="Select multiple from dropdown"
                )

                # Color Picker
                color_input = gr.ColorPicker(
                    label="Color Picker",
                    value="#FF5733",
                    info="Pick a color"
                )

                # DateTime
                datetime_input = gr.DateTime(
                    label="DateTime",
                    info="Select date and time"
                )

                # Code Input
                code_input = gr.Code(
                    label="Code Editor",
                    language="python",
                    value="def hello():\n    print('Hello, World!')",
                    lines=4
                )

        submit_btn = gr.Button("Process All Inputs", variant="primary")
        output = gr.Markdown(label="Output")

        submit_btn.click(
            fn=process_all_inputs,
            inputs=[
                text_input, number_input, slider_input, checkbox_input,
                checkboxgroup_input, radio_input, dropdown_input,
                multiselect_input, color_input, datetime_input, code_input
            ],
            outputs=output
        )

    return demo


# ============================================================================
# SECTION 3: OUTPUT COMPONENTS
# ============================================================================

def output_components_showcase():
    """
    Showcase all major output components available in Gradio.
    """

    def generate_outputs(text: str):
        # Generate various output formats
        label_output = {
            "Positive": 0.85,
            "Negative": 0.10,
            "Neutral": 0.05
        }

        highlighted_text = [
            ("This is ", None),
            ("highlighted", "important"),
            (" text with ", None),
            ("multiple", "keyword"),
            (" annotations.", None)
        ]

        json_output = {
            "input_text": text,
            "length": len(text),
            "word_count": len(text.split()),
            "timestamp": datetime.now().isoformat()
        }

        html_output = f"""
        <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
            <h3>HTML Output</h3>
            <p>You entered: <strong>{text}</strong></p>
            <p>Length: {len(text)} characters</p>
        </div>
        """

        markdown_output = f"""
## Markdown Output

Your input: **{text}**

### Statistics:
- Characters: `{len(text)}`
- Words: `{len(text.split())}`
- Lines: `{text.count(chr(10)) + 1}`
"""

        return label_output, highlighted_text, json_output, html_output, markdown_output

    with gr.Blocks(title="Output Components Showcase") as demo:
        gr.Markdown("# Output Components Showcase")
        gr.Markdown("Demonstrating various output display components")

        text_input = gr.Textbox(
            label="Enter Text",
            placeholder="Type something to see different output formats...",
            value="Hello Gradio World!"
        )

        generate_btn = gr.Button("Generate Outputs", variant="primary")

        with gr.Row():
            with gr.Column():
                # Label (Classification Results)
                label_output = gr.Label(
                    label="Label (Classification)",
                    num_top_classes=3
                )

                # Highlighted Text
                highlighted_output = gr.HighlightedText(
                    label="Highlighted Text",
                    color_map={"important": "red", "keyword": "blue"}
                )

                # JSON
                json_output = gr.JSON(label="JSON Output")

            with gr.Column():
                # HTML
                html_output = gr.HTML(label="HTML Output")

                # Markdown
                markdown_output = gr.Markdown(label="Markdown Output")

        generate_btn.click(
            fn=generate_outputs,
            inputs=text_input,
            outputs=[label_output, highlighted_output, json_output, html_output, markdown_output]
        )

    return demo


# ============================================================================
# SECTION 4: LAYOUT COMPONENTS
# ============================================================================

def layout_components_showcase():
    """
    Demonstrate layout components: Row, Column, Tab, Accordion, Group.
    """

    with gr.Blocks(title="Layout Components Showcase") as demo:
        gr.Markdown("# Layout Components Showcase")

        # Tabs
        with gr.Tabs():
            # Tab 1: Row and Column
            with gr.Tab("Row & Column"):
                gr.Markdown("### Row and Column Layout")

                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("**Column 1** (scale=1)")
                        gr.Textbox(label="Input 1", placeholder="Small column")

                    with gr.Column(scale=2):
                        gr.Markdown("**Column 2** (scale=2)")
                        gr.Textbox(label="Input 2", placeholder="Medium column")
                        gr.Textbox(label="Input 3", placeholder="Another input")

                    with gr.Column(scale=1):
                        gr.Markdown("**Column 3** (scale=1)")
                        gr.Button("Button 1")
                        gr.Button("Button 2")

                with gr.Row(equal_height=True):
                    gr.Textbox(label="Equal Height 1", lines=3)
                    gr.Textbox(label="Equal Height 2", lines=1)
                    gr.Textbox(label="Equal Height 3", lines=5)

            # Tab 2: Accordion
            with gr.Tab("Accordion"):
                gr.Markdown("### Accordion Layout")

                with gr.Accordion("Basic Settings", open=True):
                    gr.Textbox(label="Name")
                    gr.Number(label="Age")

                with gr.Accordion("Advanced Settings", open=False):
                    gr.Slider(label="Complexity", minimum=0, maximum=100)
                    gr.Checkbox(label="Enable Feature X")
                    gr.Checkbox(label="Enable Feature Y")

                with gr.Accordion("Expert Settings", open=False):
                    gr.Code(label="Custom Configuration", language="json")

            # Tab 3: Group
            with gr.Tab("Group"):
                gr.Markdown("### Group Layout")

                with gr.Group():
                    gr.Markdown("**Grouped Components** (visually connected)")
                    gr.Textbox(label="Username")
                    gr.Textbox(label="Password", type="password")
                    gr.Button("Login", variant="primary")

                gr.Markdown("---")

                with gr.Group():
                    gr.Markdown("**Another Group**")
                    gr.Number(label="Amount")
                    gr.Dropdown(label="Currency", choices=["USD", "EUR", "GBP"])

            # Tab 4: Nested Tabs
            with gr.Tab("Nested Tabs"):
                gr.Markdown("### Nested Tab Example")

                with gr.Tabs():
                    with gr.Tab("Sub-Tab A"):
                        gr.Textbox(label="Content A")
                    with gr.Tab("Sub-Tab B"):
                        gr.Textbox(label="Content B")
                    with gr.Tab("Sub-Tab C"):
                        gr.Textbox(label="Content C")

    return demo


# ============================================================================
# SECTION 5: EVENT HANDLING
# ============================================================================

def event_handling_showcase():
    """
    Demonstrate event handling: click, change, submit, then, success.
    """

    def on_text_change(text):
        return f"Text changed! Length: {len(text)}"

    def on_button_click(text):
        time.sleep(0.5)  # Simulate processing
        return f"Button clicked! You entered: {text}"

    def on_submit(text):
        return f"Submitted: {text.upper()}"

    def step1(text):
        time.sleep(0.3)
        return f"Step 1 complete: {text}"

    def step2(result):
        time.sleep(0.3)
        return f"{result} -> Step 2 complete"

    def step3(result):
        time.sleep(0.3)
        return f"{result} -> Step 3 complete (DONE!)"

    def might_fail(should_fail):
        if should_fail:
            raise ValueError("Intentional failure!")
        return "Success! This ran without errors."

    def on_success():
        return "Success handler triggered!"

    with gr.Blocks(title="Event Handling Showcase") as demo:
        gr.Markdown("# Event Handling Showcase")
        gr.Markdown("Demonstrating various event types and chaining")

        with gr.Tabs():
            # Tab 1: Basic Events
            with gr.Tab("Basic Events"):
                gr.Markdown("### Click, Change, and Submit Events")

                text_input = gr.Textbox(
                    label="Type something (change event)",
                    placeholder="Start typing..."
                )
                change_output = gr.Textbox(label="Change Event Output", interactive=False)

                text_input.change(fn=on_text_change, inputs=text_input, outputs=change_output)

                gr.Markdown("---")

                submit_input = gr.Textbox(
                    label="Press Enter to Submit",
                    placeholder="Type and press Enter..."
                )
                submit_output = gr.Textbox(label="Submit Event Output", interactive=False)

                submit_input.submit(fn=on_submit, inputs=submit_input, outputs=submit_output)

                gr.Markdown("---")

                click_input = gr.Textbox(label="Input for Button", value="Click me!")
                click_btn = gr.Button("Click Event", variant="primary")
                click_output = gr.Textbox(label="Click Event Output", interactive=False)

                click_btn.click(fn=on_button_click, inputs=click_input, outputs=click_output)

            # Tab 2: Event Chaining with .then()
            with gr.Tab("Event Chaining"):
                gr.Markdown("### Event Chaining with .then()")
                gr.Markdown("Events run sequentially, each waiting for the previous to complete.")

                chain_input = gr.Textbox(label="Input", value="Start")
                chain_btn = gr.Button("Run Chain", variant="primary")

                step1_output = gr.Textbox(label="Step 1", interactive=False)
                step2_output = gr.Textbox(label="Step 2", interactive=False)
                step3_output = gr.Textbox(label="Step 3", interactive=False)

                # Chain events with .then()
                chain_btn.click(
                    fn=step1, inputs=chain_input, outputs=step1_output
                ).then(
                    fn=step2, inputs=step1_output, outputs=step2_output
                ).then(
                    fn=step3, inputs=step2_output, outputs=step3_output
                )

            # Tab 3: Success/Error Handling
            with gr.Tab("Success/Error"):
                gr.Markdown("### Success and Error Handling")
                gr.Markdown("Use `.success()` to run code only when previous event succeeds.")

                fail_checkbox = gr.Checkbox(label="Should the function fail?", value=False)
                try_btn = gr.Button("Try Operation", variant="primary")
                result_output = gr.Textbox(label="Result", interactive=False)
                success_output = gr.Textbox(label="Success Handler", interactive=False)

                try_btn.click(
                    fn=might_fail, inputs=fail_checkbox, outputs=result_output
                ).success(
                    fn=on_success, outputs=success_output
                )

            # Tab 4: Multiple Triggers
            with gr.Tab("Multiple Triggers"):
                gr.Markdown("### gr.on() - Multiple Event Triggers")
                gr.Markdown("Bind one function to multiple events.")

                input1 = gr.Textbox(label="Input 1")
                input2 = gr.Textbox(label="Input 2")
                btn = gr.Button("Also triggers!")
                multi_output = gr.Textbox(label="Output", interactive=False)

                @gr.on(triggers=[input1.change, input2.change, btn.click], inputs=[input1, input2], outputs=multi_output)
                def combined_handler(t1, t2):
                    return f"Combined: {t1} + {t2}"

    return demo


# ============================================================================
# SECTION 6: STATE MANAGEMENT
# ============================================================================

def state_management_showcase():
    """
    Demonstrate state management: gr.State for session state.
    """

    def add_to_history(text, history):
        if history is None:
            history = []
        if text.strip():
            history.append({
                "text": text,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
        return history, format_history(history), ""

    def format_history(history):
        if not history:
            return "No items yet."
        lines = ["## History\n"]
        for i, item in enumerate(history, 1):
            lines.append(f"{i}. **{item['text']}** (at {item['timestamp']})")
        return "\n".join(lines)

    def clear_history():
        return [], "History cleared."

    def increment_counter(count):
        return count + 1, f"Count: {count + 1}"

    def decrement_counter(count):
        return max(0, count - 1), f"Count: {max(0, count - 1)}"

    def reset_counter():
        return 0, "Count: 0"

    with gr.Blocks(title="State Management Showcase") as demo:
        gr.Markdown("# State Management Showcase")
        gr.Markdown("gr.State maintains data across interactions within a session")

        with gr.Tabs():
            # Tab 1: History Example
            with gr.Tab("Session History"):
                gr.Markdown("### Persistent History (Session State)")

                # State to store history
                history_state = gr.State([])

                with gr.Row():
                    text_input = gr.Textbox(
                        label="Add to History",
                        placeholder="Type something and click Add..."
                    )
                    add_btn = gr.Button("Add", variant="primary")

                history_display = gr.Markdown("No items yet.")
                clear_btn = gr.Button("Clear History", variant="secondary")

                add_btn.click(
                    fn=add_to_history,
                    inputs=[text_input, history_state],
                    outputs=[history_state, history_display, text_input]
                )

                clear_btn.click(
                    fn=clear_history,
                    outputs=[history_state, history_display]
                )

            # Tab 2: Counter Example
            with gr.Tab("Counter"):
                gr.Markdown("### Counter with State")

                # State for counter
                counter_state = gr.State(0)

                counter_display = gr.Markdown("Count: 0")

                with gr.Row():
                    dec_btn = gr.Button("-", variant="secondary")
                    reset_btn = gr.Button("Reset")
                    inc_btn = gr.Button("+", variant="primary")

                inc_btn.click(
                    fn=increment_counter,
                    inputs=counter_state,
                    outputs=[counter_state, counter_display]
                )

                dec_btn.click(
                    fn=decrement_counter,
                    inputs=counter_state,
                    outputs=[counter_state, counter_display]
                )

                reset_btn.click(
                    fn=reset_counter,
                    outputs=[counter_state, counter_display]
                )

            # Tab 3: Complex State
            with gr.Tab("Complex State"):
                gr.Markdown("### Complex State Object")

                # State with dictionary
                app_state = gr.State({
                    "items": [],
                    "settings": {"dark_mode": False, "notifications": True}
                })

                def add_item(name, state):
                    state["items"].append(name)
                    return state, f"Items: {', '.join(state['items']) or 'None'}"

                def toggle_setting(setting, state):
                    state["settings"][setting] = not state["settings"][setting]
                    status = "ON" if state["settings"][setting] else "OFF"
                    return state, f"{setting}: {status}"

                item_input = gr.Textbox(label="Item Name")
                add_item_btn = gr.Button("Add Item")
                items_display = gr.Textbox(label="Items", interactive=False, value="Items: None")

                add_item_btn.click(
                    fn=add_item,
                    inputs=[item_input, app_state],
                    outputs=[app_state, items_display]
                )

                gr.Markdown("---")

                with gr.Row():
                    dark_btn = gr.Button("Toggle Dark Mode")
                    notif_btn = gr.Button("Toggle Notifications")

                setting_display = gr.Textbox(label="Setting Status", interactive=False)

                dark_btn.click(
                    fn=lambda s: toggle_setting("dark_mode", s),
                    inputs=app_state,
                    outputs=[app_state, setting_display]
                )

                notif_btn.click(
                    fn=lambda s: toggle_setting("notifications", s),
                    inputs=app_state,
                    outputs=[app_state, setting_display]
                )

    return demo


# ============================================================================
# SECTION 7: THEMING
# ============================================================================

def theming_showcase():
    """
    Demonstrate Gradio theming capabilities.
    """

    def echo(text):
        return text

    # Create examples with different built-in themes
    with gr.Blocks(theme=gr.themes.Default()) as demo:
        gr.Markdown("# Theming Showcase")
        gr.Markdown("Gradio supports built-in themes and custom theming")

        with gr.Tabs():
            # Tab 1: Built-in Themes Preview
            with gr.Tab("Built-in Themes"):
                gr.Markdown("""
### Available Built-in Themes

Gradio comes with several pre-built themes:

1. **gr.themes.Default()** - The standard Gradio theme
2. **gr.themes.Soft()** - Softer colors and rounded corners
3. **gr.themes.Monochrome()** - Black and white minimalist
4. **gr.themes.Glass()** - Glassmorphism style
5. **gr.themes.Base()** - Simple base theme for customization

You can apply a theme to any Blocks app:
```python
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    ...
```

Or load themes from Hugging Face Hub:
```python
with gr.Blocks(theme="gradio/seafoam") as demo:
    ...
```
""")

                gr.Textbox(label="Sample Input", placeholder="This uses Default theme")
                gr.Button("Sample Button", variant="primary")

            # Tab 2: Custom Theme
            with gr.Tab("Custom Theme"):
                gr.Markdown("""
### Custom Theme Example

You can create custom themes by subclassing `gr.themes.Base`:

```python
custom_theme = gr.themes.Base(
    primary_hue="indigo",
    secondary_hue="purple",
    neutral_hue="slate",
    font=gr.themes.GoogleFont("Roboto"),
    font_mono=gr.themes.GoogleFont("Roboto Mono"),
).set(
    body_background_fill="*neutral_50",
    button_primary_background_fill="*primary_500",
    button_primary_text_color="white",
)
```
""")

                with gr.Row():
                    gr.Textbox(label="Primary Input")
                    gr.Textbox(label="Secondary Input")

                with gr.Row():
                    gr.Button("Primary", variant="primary")
                    gr.Button("Secondary", variant="secondary")
                    gr.Button("Stop", variant="stop")

            # Tab 3: Theme Components
            with gr.Tab("Theme Components"):
                gr.Markdown("### Theme Affects All Components")

                with gr.Row():
                    with gr.Column():
                        gr.Textbox(label="Textbox")
                        gr.Number(label="Number", value=42)
                        gr.Slider(label="Slider", value=50)

                    with gr.Column():
                        gr.Checkbox(label="Checkbox", value=True)
                        gr.Radio(["A", "B", "C"], label="Radio", value="A")
                        gr.Dropdown(["X", "Y", "Z"], label="Dropdown", value="X")

                with gr.Accordion("Accordion"):
                    gr.Markdown("Content inside accordion")
                    gr.Code("print('hello')", language="python")

    return demo


# ============================================================================
# SECTION 8: MEDIA COMPONENTS
# ============================================================================

def media_components_showcase():
    """
    Demonstrate media components: Image, Audio, Video, Gallery, File.
    """

    def create_sample_image():
        """Create a sample numpy image."""
        # Create a gradient image
        img = np.zeros((256, 256, 3), dtype=np.uint8)
        for i in range(256):
            for j in range(256):
                img[i, j] = [i, j, 128]
        return img

    def process_image(image):
        if image is None:
            return None, "No image uploaded"
        # Simple image processing - invert colors
        inverted = 255 - image
        return inverted, f"Image shape: {image.shape}"

    def generate_gallery():
        """Generate sample images for gallery."""
        images = []
        colors = [
            [255, 0, 0],    # Red
            [0, 255, 0],    # Green
            [0, 0, 255],    # Blue
            [255, 255, 0],  # Yellow
            [255, 0, 255],  # Magenta
            [0, 255, 255],  # Cyan
        ]
        for color in colors:
            img = np.full((100, 100, 3), color, dtype=np.uint8)
            images.append(img)
        return images

    with gr.Blocks(title="Media Components Showcase") as demo:
        gr.Markdown("# Media Components Showcase")
        gr.Markdown("Image, Audio, Video, Gallery, and File components")

        with gr.Tabs():
            # Tab 1: Image
            with gr.Tab("Image"):
                gr.Markdown("### Image Component")

                with gr.Row():
                    with gr.Column():
                        image_input = gr.Image(
                            label="Upload Image",
                            type="numpy",
                            sources=["upload", "clipboard"],
                            height=300
                        )
                        process_btn = gr.Button("Process Image", variant="primary")

                    with gr.Column():
                        image_output = gr.Image(label="Processed Image", height=300)
                        image_info = gr.Textbox(label="Image Info", interactive=False)

                process_btn.click(
                    fn=process_image,
                    inputs=image_input,
                    outputs=[image_output, image_info]
                )

                gr.Markdown("---")
                gr.Markdown("**Image Display Options:**")

                with gr.Row():
                    gr.Image(
                        value=create_sample_image(),
                        label="Generated Image",
                        height=150,
                        width=150
                    )

            # Tab 2: Gallery
            with gr.Tab("Gallery"):
                gr.Markdown("### Gallery Component")

                gallery = gr.Gallery(
                    label="Image Gallery",
                    columns=3,
                    rows=2,
                    height="auto",
                    object_fit="contain"
                )

                generate_btn = gr.Button("Generate Sample Gallery", variant="primary")
                generate_btn.click(fn=generate_gallery, outputs=gallery)

                gr.Markdown("""
**Gallery Features:**
- Grid layout with customizable rows/columns
- Click to enlarge images
- Supports captions
- Multiple selection modes
""")

            # Tab 3: Audio
            with gr.Tab("Audio"):
                gr.Markdown("### Audio Component")

                audio_input = gr.Audio(
                    label="Upload or Record Audio",
                    sources=["upload", "microphone"],
                    type="filepath"
                )

                audio_output = gr.Audio(
                    label="Audio Output",
                    type="filepath"
                )

                gr.Markdown("""
**Audio Features:**
- Upload audio files
- Record from microphone
- Playback controls
- Waveform visualization
- Supports various formats (mp3, wav, etc.)
""")

            # Tab 4: Video
            with gr.Tab("Video"):
                gr.Markdown("### Video Component")

                video_input = gr.Video(
                    label="Upload Video",
                    sources=["upload"]
                )

                gr.Markdown("""
**Video Features:**
- Upload video files
- Playback with controls
- Supports webcam capture
- Various format support
""")

            # Tab 5: File
            with gr.Tab("File"):
                gr.Markdown("### File Component")

                file_input = gr.File(
                    label="Upload Files",
                    file_count="multiple",
                    file_types=[".txt", ".pdf", ".csv", ".json"]
                )

                def process_files(files):
                    if not files:
                        return "No files uploaded"
                    info = []
                    for f in files:
                        info.append(f"- {f.name}")
                    return "Uploaded files:\n" + "\n".join(info)

                file_output = gr.Textbox(label="File Info", interactive=False)
                file_input.change(fn=process_files, inputs=file_input, outputs=file_output)

                gr.Markdown("""
**File Features:**
- Single or multiple file upload
- File type filtering
- Progress indication
- Download support for outputs
""")

    return demo


# ============================================================================
# SECTION 9: DATA COMPONENTS
# ============================================================================

def data_components_showcase():
    """
    Demonstrate data components: DataFrame, JSON, Plot.
    """

    def generate_dataframe():
        """Generate a sample DataFrame."""
        data = {
            "Name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "Age": [25, 30, 35, 28, 32],
            "City": ["NYC", "LA", "Chicago", "Boston", "Seattle"],
            "Score": [85.5, 92.3, 78.9, 88.1, 95.7],
            "Active": [True, True, False, True, False]
        }
        return pd.DataFrame(data)

    def update_dataframe(df):
        """Process DataFrame and return statistics."""
        if df is None or df.empty:
            return "No data"
        stats = f"""
### DataFrame Statistics
- **Rows:** {len(df)}
- **Columns:** {len(df.columns)}
- **Column Types:** {dict(df.dtypes)}
"""
        return stats

    def generate_plot_data():
        """Generate data for plotting."""
        x = np.linspace(0, 10, 100)
        return pd.DataFrame({
            "x": x,
            "sin": np.sin(x),
            "cos": np.cos(x)
        })

    with gr.Blocks(title="Data Components Showcase") as demo:
        gr.Markdown("# Data Components Showcase")
        gr.Markdown("DataFrame, JSON, and Plot components for data display")

        with gr.Tabs():
            # Tab 1: DataFrame
            with gr.Tab("DataFrame"):
                gr.Markdown("### DataFrame Component")
                gr.Markdown("Interactive data table with editing capabilities")

                df_component = gr.Dataframe(
                    label="Editable DataFrame",
                    headers=["Name", "Age", "City", "Score", "Active"],
                    datatype=["str", "number", "str", "number", "bool"],
                    row_count=5,
                    col_count=(5, "fixed"),
                    interactive=True
                )

                with gr.Row():
                    load_btn = gr.Button("Load Sample Data", variant="primary")
                    analyze_btn = gr.Button("Analyze Data")

                stats_output = gr.Markdown()

                load_btn.click(fn=generate_dataframe, outputs=df_component)
                analyze_btn.click(fn=update_dataframe, inputs=df_component, outputs=stats_output)

            # Tab 2: JSON
            with gr.Tab("JSON"):
                gr.Markdown("### JSON Component")
                gr.Markdown("Display and interact with JSON data")

                json_input = gr.Code(
                    label="Edit JSON",
                    language="json",
                    value='''{
    "name": "Gradio",
    "version": "4.0",
    "features": ["Interface", "Blocks", "Components"],
    "settings": {
        "debug": true,
        "cache": false
    }
}'''
                )

                def parse_json(json_str):
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError as e:
                        return {"error": str(e)}

                parse_btn = gr.Button("Parse & Display", variant="primary")
                json_output = gr.JSON(label="Parsed JSON")

                parse_btn.click(fn=parse_json, inputs=json_input, outputs=json_output)

            # Tab 3: Line Plot
            with gr.Tab("Line Plot"):
                gr.Markdown("### LinePlot Component")

                plot_data = gr.State(generate_plot_data())

                line_plot = gr.LinePlot(
                    x="x",
                    y="sin",
                    title="Trigonometric Functions",
                    x_title="X",
                    y_title="Y",
                    height=400,
                    width=600
                )

                def update_plot(data, y_col):
                    return gr.LinePlot(value=data, x="x", y=y_col)

                with gr.Row():
                    y_selector = gr.Radio(
                        choices=["sin", "cos"],
                        value="sin",
                        label="Select Function"
                    )

                refresh_btn = gr.Button("Refresh Plot", variant="primary")
                refresh_btn.click(
                    fn=lambda d, y: d,
                    inputs=[plot_data, y_selector],
                    outputs=line_plot
                )

            # Tab 4: Scatter Plot
            with gr.Tab("Scatter Plot"):
                gr.Markdown("### ScatterPlot Component")

                def generate_scatter_data():
                    n = 100
                    return pd.DataFrame({
                        "x": np.random.randn(n) * 10,
                        "y": np.random.randn(n) * 10,
                        "size": np.random.rand(n) * 50,
                        "category": np.random.choice(["A", "B", "C"], n)
                    })

                scatter_data = generate_scatter_data()

                scatter_plot = gr.ScatterPlot(
                    value=scatter_data,
                    x="x",
                    y="y",
                    color="category",
                    title="Random Scatter Plot",
                    height=400,
                    width=600
                )

                regen_btn = gr.Button("Regenerate Data", variant="primary")
                regen_btn.click(fn=generate_scatter_data, outputs=scatter_plot)

    return demo


# ============================================================================
# SECTION 10: CHATBOT
# ============================================================================

def chatbot_showcase():
    """
    Demonstrate Chatbot component and conversational interfaces.
    """

    def respond(message, chat_history):
        """Simple echo bot with some intelligence."""
        if not message.strip():
            return "", chat_history

        # Simple response logic
        responses = {
            "hello": "Hello! How can I help you today?",
            "hi": "Hi there! What's on your mind?",
            "bye": "Goodbye! Have a great day!",
            "help": "I'm a demo chatbot. Try saying hello, asking about the weather, or just chat!",
            "weather": "I don't have real weather data, but it's always sunny in Gradio land!",
            "gradio": "Gradio is an amazing library for building ML demos and web apps!",
        }

        # Check for keywords
        response = None
        for keyword, reply in responses.items():
            if keyword in message.lower():
                response = reply
                break

        if response is None:
            response = f"You said: '{message}'. I'm a simple echo bot - try saying 'help' for options!"

        chat_history.append((message, response))
        return "", chat_history

    def clear_chat():
        return []

    with gr.Blocks(title="Chatbot Showcase") as demo:
        gr.Markdown("# Chatbot Showcase")
        gr.Markdown("Conversational interfaces with gr.Chatbot")

        with gr.Tabs():
            # Tab 1: Basic Chatbot
            with gr.Tab("Basic Chatbot"):
                gr.Markdown("### Simple Chatbot")

                chatbot = gr.Chatbot(
                    label="Chat",
                    height=400,
                    bubble_full_width=False
                )

                with gr.Row():
                    msg = gr.Textbox(
                        label="Message",
                        placeholder="Type a message...",
                        scale=4
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)

                clear_btn = gr.Button("Clear Chat")

                msg.submit(fn=respond, inputs=[msg, chatbot], outputs=[msg, chatbot])
                submit_btn.click(fn=respond, inputs=[msg, chatbot], outputs=[msg, chatbot])
                clear_btn.click(fn=clear_chat, outputs=chatbot)

            # Tab 2: Chatbot Styling
            with gr.Tab("Styled Chatbot"):
                gr.Markdown("### Chatbot with Custom Styling")

                styled_chatbot = gr.Chatbot(
                    value=[
                        ("Hello!", "Hi! I'm a styled chatbot."),
                        ("What can you do?", "I demonstrate Gradio's chatbot styling options!"),
                    ],
                    label="Styled Chat",
                    height=300,
                    avatar_images=(None, "https://avatars.githubusercontent.com/u/51063788?s=200&v=4"),
                    bubble_full_width=False,
                    show_copy_button=True
                )

                gr.Markdown("""
**Chatbot Features:**
- Custom avatars for user/assistant
- Copy button on messages
- Bubble styling options
- Markdown support in messages
- Code block support
- Image support
""")

            # Tab 3: ChatInterface
            with gr.Tab("ChatInterface"):
                gr.Markdown("### gr.ChatInterface - Simplified Chat Builder")
                gr.Markdown("""
`gr.ChatInterface` is a high-level component that wraps common chatbot patterns:

```python
def respond(message, history):
    return f"You said: {message}"

gr.ChatInterface(
    fn=respond,
    title="My Chatbot",
    examples=["Hello", "How are you?"],
    theme="soft"
).launch()
```

**Features:**
- Automatic history management
- Built-in examples
- Retry/Undo buttons
- Streaming support
""")

    return demo


# ============================================================================
# SECTION 11: EXAMPLES COMPONENT
# ============================================================================

def examples_component_showcase():
    """
    Demonstrate the Examples component for pre-populated inputs.
    """

    def process_example(text, number, choice):
        return f"Text: {text}\nNumber: {number}\nChoice: {choice}"

    with gr.Blocks(title="Examples Component Showcase") as demo:
        gr.Markdown("# Examples Component Showcase")
        gr.Markdown("Pre-populate inputs with clickable examples")

        with gr.Tabs():
            # Tab 1: Basic Examples
            with gr.Tab("Basic Examples"):
                gr.Markdown("### Click an example to populate inputs")

                text_input = gr.Textbox(label="Text Input")
                number_input = gr.Number(label="Number Input")
                choice_input = gr.Dropdown(
                    choices=["Option A", "Option B", "Option C"],
                    label="Choice"
                )

                submit_btn = gr.Button("Process", variant="primary")
                output = gr.Textbox(label="Output", interactive=False)

                # Examples component
                gr.Examples(
                    examples=[
                        ["Hello World", 42, "Option A"],
                        ["Gradio Example", 100, "Option B"],
                        ["Machine Learning", 256, "Option C"],
                        ["Deep Learning", 512, "Option A"],
                    ],
                    inputs=[text_input, number_input, choice_input],
                    label="Click an example"
                )

                submit_btn.click(
                    fn=process_example,
                    inputs=[text_input, number_input, choice_input],
                    outputs=output
                )

            # Tab 2: Cached Examples
            with gr.Tab("Cached Examples"):
                gr.Markdown("### Cached Examples")
                gr.Markdown("""
Examples can be cached to speed up loading:

```python
gr.Examples(
    examples=[...],
    inputs=[...],
    outputs=[...],
    fn=process_fn,
    cache_examples=True  # Pre-compute outputs
)
```

This is useful when:
- Processing is slow
- You want instant preview
- Examples are fixed
""")

            # Tab 3: Examples from Directory
            with gr.Tab("Directory Examples"):
                gr.Markdown("### Load Examples from Directory")
                gr.Markdown("""
You can load examples from a directory:

```python
gr.Examples(
    examples="path/to/examples/folder",
    inputs=[image_input, text_input],
)
```

The directory structure should match the input components:
```
examples/
  example1/
    image.png
    text.txt
  example2/
    image.png
    text.txt
```

This is useful for:
- Large example sets
- Image/file examples
- Version-controlled examples
""")

    return demo


# ============================================================================
# SECTION 12: ADVANCED FEATURES
# ============================================================================

def advanced_features_showcase():
    """
    Demonstrate advanced Gradio features.
    """

    with gr.Blocks(title="Advanced Features Showcase") as demo:
        gr.Markdown("# Advanced Features Showcase")

        with gr.Tabs():
            # Tab 1: Progress Bars
            with gr.Tab("Progress"):
                gr.Markdown("### Progress Bars")

                def long_process(progress=gr.Progress()):
                    progress(0, desc="Starting...")
                    results = []
                    for i in progress.tqdm(range(10), desc="Processing"):
                        time.sleep(0.3)
                        results.append(f"Step {i+1}")
                    return "\n".join(results)

                progress_btn = gr.Button("Start Long Process", variant="primary")
                progress_output = gr.Textbox(label="Output", lines=10, interactive=False)

                progress_btn.click(fn=long_process, outputs=progress_output)

                gr.Markdown("""
**Progress Features:**
- Track progress with `gr.Progress()`
- Use `progress.tqdm()` for iterables
- Custom descriptions
- Nested progress bars
""")

            # Tab 2: Render Decorator
            with gr.Tab("Dynamic UI"):
                gr.Markdown("### gr.render - Dynamic UI Updates")

                num_inputs = gr.Slider(
                    minimum=1,
                    maximum=5,
                    value=3,
                    step=1,
                    label="Number of Inputs"
                )

                @gr.render(inputs=num_inputs)
                def render_inputs(n):
                    textboxes = []
                    for i in range(int(n)):
                        t = gr.Textbox(label=f"Input {i+1}")
                        textboxes.append(t)

                    def combine(*texts):
                        return " + ".join(texts)

                    if textboxes:
                        btn = gr.Button("Combine")
                        out = gr.Textbox(label="Combined")
                        btn.click(fn=combine, inputs=textboxes, outputs=out)

                gr.Markdown("""
**Dynamic UI Features:**
- Conditionally render components
- React to input changes
- Create dynamic forms
- Adjust UI based on selections
""")

            # Tab 3: Queueing
            with gr.Tab("Queueing"):
                gr.Markdown("### Event Queue System")
                gr.Markdown("""
Gradio's queue system manages concurrent requests:

```python
demo = gr.Blocks()
# ...
demo.queue(
    max_size=10,           # Max queue length
    default_concurrency_limit=1  # Concurrent requests
)
demo.launch()
```

**Queue Features:**
- Automatic request ordering
- Concurrency control
- Progress tracking
- WebSocket streaming
- Prevents server overload

**Status Indicators:**
- Queue position shown to users
- ETA estimates
- Cancellation support
""")

            # Tab 4: Custom CSS/JS
            with gr.Tab("Custom CSS/JS"):
                gr.Markdown("### Custom Styling")
                gr.Markdown("""
Add custom CSS to style your app:

```python
css = '''
.custom-button {
    background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
    border: none;
    color: white;
}
'''

with gr.Blocks(css=css) as demo:
    btn = gr.Button("Styled", elem_classes=["custom-button"])
```

Add custom JavaScript:

```python
js = '''
function() {
    console.log("Page loaded!");
}
'''

with gr.Blocks(js=js) as demo:
    ...
```

**Features:**
- Element-specific classes with `elem_classes`
- Element IDs with `elem_id`
- Full CSS customization
- JavaScript event handlers
""")

            # Tab 5: API & Programmatic Access
            with gr.Tab("API Access"):
                gr.Markdown("### Programmatic API Access")
                gr.Markdown("""
Every Gradio app automatically gets an API:

**View API docs:**
```
http://localhost:7860/?view=api
```

**Python Client:**
```python
from gradio_client import Client

client = Client("http://localhost:7860")
result = client.predict(
    "Hello",           # Input
    api_name="/predict"
)
```

**curl:**
```bash
curl -X POST http://localhost:7860/call/predict \\
  -H "Content-Type: application/json" \\
  -d '{"data": ["Hello"]}'
```

**Features:**
- Auto-generated API docs
- Python/JavaScript clients
- REST API endpoints
- File upload/download
- Async support
""")

            # Tab 6: Flagging
            with gr.Tab("Flagging"):
                gr.Markdown("### Flagging & Data Collection")

                def predict(text):
                    return text.upper()

                flag_input = gr.Textbox(label="Input")
                flag_output = gr.Textbox(label="Output")
                flag_btn = gr.Button("Process")

                flag_btn.click(fn=predict, inputs=flag_input, outputs=flag_output)

                gr.Markdown("""
**Flagging allows users to save examples:**

```python
gr.Interface(
    fn=predict,
    inputs="text",
    outputs="text",
    flagging_mode="manual",  # or "auto", "never"
    flagging_dir="flagged"
)
```

**Use cases:**
- Collect user feedback
- Identify edge cases
- Build training datasets
- Debug production issues
""")

    return demo


# ============================================================================
# SECTION 13: INTEGRATION EXAMPLES
# ============================================================================

def integration_examples_showcase():
    """
    Demonstrate integration with external services and APIs.
    """

    with gr.Blocks(title="Integration Examples") as demo:
        gr.Markdown("# Integration Examples")
        gr.Markdown("Patterns for integrating Gradio with various services")

        with gr.Tabs():
            # Tab 1: FastAPI Integration
            with gr.Tab("FastAPI"):
                gr.Markdown("### FastAPI Integration")
                gr.Markdown("""
Mount Gradio inside a FastAPI app:

```python
from fastapi import FastAPI
import gradio as gr

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok"}

# Create Gradio app
with gr.Blocks() as demo:
    gr.Markdown("# My App")
    ...

# Mount at /gradio
app = gr.mount_gradio_app(app, demo, path="/gradio")

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Benefits:**
- Combine REST APIs with UI
- Shared authentication
- Custom middleware
- Mixed endpoints
""")

            # Tab 2: Hugging Face Hub
            with gr.Tab("Hugging Face"):
                gr.Markdown("### Hugging Face Hub Integration")
                gr.Markdown("""
**Load Models from Hub:**

```python
import gradio as gr
from transformers import pipeline

# Load sentiment analysis model
classifier = pipeline("sentiment-analysis")

def analyze(text):
    result = classifier(text)[0]
    return {result["label"]: result["score"]}

gr.Interface(
    fn=analyze,
    inputs="text",
    outputs="label",
    title="Sentiment Analysis"
).launch()
```

**Deploy to Spaces:**

```python
# Save as app.py in a Hugging Face Space
# It will automatically deploy!

demo.launch()  # No need for special config
```

**Load Spaces as Components:**

```python
gr.load("huggingface/spaces/username/my-space")
```
""")

            # Tab 3: Database Integration
            with gr.Tab("Database"):
                gr.Markdown("### Database Integration")
                gr.Markdown("""
**SQLite Example:**

```python
import sqlite3
import gradio as gr

def query_db(sql):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.close()
    return results

gr.Interface(
    fn=query_db,
    inputs=gr.Textbox(label="SQL Query"),
    outputs=gr.Dataframe(label="Results")
).launch()
```

**Best Practices:**
- Use connection pooling
- Sanitize inputs (prevent SQL injection)
- Handle errors gracefully
- Consider async for performance
""")

            # Tab 4: Authentication
            with gr.Tab("Authentication"):
                gr.Markdown("### Authentication Options")
                gr.Markdown("""
**Simple Password:**

```python
demo.launch(
    auth=("username", "password")
)
```

**Multiple Users:**

```python
demo.launch(
    auth=[
        ("user1", "pass1"),
        ("user2", "pass2")
    ]
)
```

**Custom Auth Function:**

```python
def auth_fn(username, password):
    # Check against database
    return verify_credentials(username, password)

demo.launch(auth=auth_fn)
```

**OAuth (Hugging Face Spaces):**

```python
demo.launch(
    auth="oauth"  # Uses HF OAuth
)
```
""")

    return demo


# ============================================================================
# MAIN APPLICATION - COMBINES ALL SHOWCASES
# ============================================================================

def create_main_showcase():
    """
    Create the main showcase application combining all examples.
    """

    with gr.Blocks(
        title="Gradio Complete Showcase",
        theme=gr.themes.Soft()
    ) as demo:
        gr.Markdown("""
# Gradio Complete Showcase

Welcome to the comprehensive Gradio showcase! This application demonstrates
all major features and components available in Gradio.

**Navigation:** Use the tabs below to explore different feature categories.
""")

        with gr.Tabs():
            with gr.Tab("1. Basic Interface"):
                basic_interface_example()

            with gr.Tab("2. Input Components"):
                input_components_showcase()

            with gr.Tab("3. Output Components"):
                output_components_showcase()

            with gr.Tab("4. Layout"):
                layout_components_showcase()

            with gr.Tab("5. Events"):
                event_handling_showcase()

            with gr.Tab("6. State"):
                state_management_showcase()

            with gr.Tab("7. Themes"):
                theming_showcase()

            with gr.Tab("8. Media"):
                media_components_showcase()

            with gr.Tab("9. Data"):
                data_components_showcase()

            with gr.Tab("10. Chatbot"):
                chatbot_showcase()

            with gr.Tab("11. Examples"):
                examples_component_showcase()

            with gr.Tab("12. Advanced"):
                advanced_features_showcase()

            with gr.Tab("13. Integration"):
                integration_examples_showcase()

        gr.Markdown("""
---
### Resources

- [Gradio Documentation](https://www.gradio.app/docs)
- [Gradio Guides](https://www.gradio.app/guides)
- [Gradio GitHub](https://github.com/gradio-app/gradio)
- [Hugging Face Spaces](https://huggingface.co/spaces)
""")

    return demo


# ============================================================================
# STANDALONE EXAMPLES (can be run individually)
# ============================================================================

def run_standalone_example(name: str):
    """Run a standalone example by name."""
    examples = {
        "basic": basic_interface_example,
        "inputs": input_components_showcase,
        "outputs": output_components_showcase,
        "layout": layout_components_showcase,
        "events": event_handling_showcase,
        "state": state_management_showcase,
        "themes": theming_showcase,
        "media": media_components_showcase,
        "data": data_components_showcase,
        "chatbot": chatbot_showcase,
        "examples": examples_component_showcase,
        "advanced": advanced_features_showcase,
        "integration": integration_examples_showcase,
        "all": create_main_showcase,
    }

    if name not in examples:
        print(f"Unknown example: {name}")
        print(f"Available examples: {', '.join(examples.keys())}")
        return

    demo = examples[name]()
    demo.launch()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Run specific example
        example_name = sys.argv[1]
        run_standalone_example(example_name)
    else:
        # Run full showcase
        demo = create_main_showcase()
        demo.queue()  # Enable queue for progress bars and streaming
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )
