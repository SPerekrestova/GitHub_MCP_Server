# Gradio Showcase

A comprehensive demonstration of all major Gradio features and components.

## Quick Start

```bash
# Install dependencies
pip install gradio>=4.0.0 numpy pandas matplotlib pillow

# Run the full showcase
python gradio_showcase.py

# Open in browser
# http://localhost:7860
```

## Run Individual Examples

```bash
python gradio_showcase.py <example_name>
```

**Available examples:**
| Name | Description |
|------|-------------|
| `basic` | Basic gr.Interface |
| `inputs` | All input components |
| `outputs` | All output components |
| `layout` | Row, Column, Tab, Accordion |
| `events` | Click, change, submit, chaining |
| `state` | Session state management |
| `themes` | Built-in and custom themes |
| `media` | Image, Audio, Video, Gallery |
| `data` | DataFrame, JSON, Plot |
| `chatbot` | Conversational interfaces |
| `examples` | gr.Examples component |
| `advanced` | Progress, dynamic UI, queuing |
| `integration` | FastAPI, HF Hub, databases |
| `all` | Full showcase (default) |

## Features Covered

### Input Components
- Textbox, Number, Slider
- Checkbox, CheckboxGroup
- Radio, Dropdown (single/multi)
- ColorPicker, DateTime
- Code editor

### Output Components
- Label (classification)
- HighlightedText
- JSON, HTML, Markdown

### Layout
- Row, Column (with scale)
- Tabs (nested)
- Accordion
- Group

### Events
- click, change, submit
- Event chaining with `.then()`
- Error handling with `.success()`
- Multiple triggers with `gr.on()`

### State
- Session state with `gr.State()`
- Complex state objects
- Counter and history examples

### Media
- Image upload/processing
- Gallery display
- Audio (upload/record)
- Video upload
- File handling

### Data
- DataFrame (editable)
- JSON display
- LinePlot, ScatterPlot

### Advanced
- Progress bars
- Dynamic UI with `gr.render`
- Queue system
- Custom CSS/JS
- API access
- Flagging

### Integration
- FastAPI mounting
- Hugging Face Hub
- Database patterns
- Authentication
