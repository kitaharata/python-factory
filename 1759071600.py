import json
import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

json_schema = {
    "type": "object",
    "properties": {
        "images": {
            "type": "array",
            "description": "Pyxel Image Data Sets (pyxel.images[i].set)",
            "items": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "Pyxel image bank index (0, 1, or 2)",
                        "minimum": 0,
                        "maximum": 2,
                    },
                    "x": {"type": "integer", "description": "X coordinate (0-255)", "minimum": 0, "maximum": 255},
                    "y": {"type": "integer", "description": "Y coordinate (0-255)", "minimum": 0, "maximum": 255},
                    "data": {
                        "type": "array",
                        "description": "Hexadecimal pixel data strings (color index 0-f).",
                        "items": {"type": "string", "pattern": "^[0-9a-fA-F]*$"},
                    },
                },
                "required": ["index", "x", "y", "data"],
            },
        },
        "tilemaps": {
            "type": "array",
            "description": "Pyxel Tilemap Data Sets (pyxel.tilemaps[i].set)",
            "items": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "Pyxel tilemap bank index (0-7)",
                        "minimum": 0,
                        "maximum": 7,
                    },
                    "x": {
                        "type": "integer",
                        "description": "X coordinate in tiles (0-31)",
                        "minimum": 0,
                        "maximum": 31,
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate in tiles (0-31)",
                        "minimum": 0,
                        "maximum": 31,
                    },
                    "data": {
                        "type": "array",
                        "description": "Hexadecimal strings of tile indices (2 chars per tile).",
                        "items": {"type": "string", "pattern": "^[0-9a-fA-F]*$"},
                    },
                },
                "required": ["index", "x", "y", "data"],
            },
        },
        "sounds": {
            "type": "array",
            "description": "Pyxel Sound Data Sets (pyxel.sounds[i].set)",
            "items": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "Pyxel sound index (0-63)",
                        "minimum": 0,
                        "maximum": 63,
                    },
                    "notes": {"type": "string", "description": "Notes string (e.g., 'C2E2G2')"},
                    "tones": {"type": "string", "description": "Tones string (0-3)", "pattern": "^[0-3]*$"},
                    "volumes": {"type": "string", "description": "Volumes string (0-7)", "pattern": "^[0-7]*$"},
                    "effects": {"type": "string", "description": "Effects string (0-3)", "pattern": "^[0-3]*$"},
                    "speed": {"type": "integer", "description": "Sound speed (1-99)", "minimum": 1, "maximum": 99},
                },
                "required": ["index", "notes", "tones", "volumes", "effects", "speed"],
            },
        },
        "musics": {
            "type": "array",
            "description": "Pyxel Music Data Sets (pyxel.musics[i].set)",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer", "description": "Pyxel music index (0-7)", "minimum": 0, "maximum": 7},
                    "sequences": {
                        "type": "array",
                        "description": "Array of sound index sequences, corresponding to Pyxel music channels.",
                        "items": {"type": "array", "items": {"type": "integer", "minimum": -1, "maximum": 63}},
                        "minItems": 4,
                        "maxItems": 4,
                    },
                },
                "required": ["index", "sequences"],
            },
        },
    },
    "required": ["images", "tilemaps", "sounds", "musics"],
}

system_instruction = """You are an expert Pyxel asset configuration generator. Your task is to produce a JSON object defining assets (images, tilemaps, sounds, musics) based on the user's request, adhering strictly to the provided JSON schema.

rules:
1. The output MUST be a single, valid JSON object.
2. The JSON object MUST contain the top-level keys: 'images', 'tilemaps', 'sounds', and 'musics'. Use an empty array ([]) if no data is required for a key.
3. Do NOT include any explanatory text or supplementary commentary outside of the JSON block.
4. Utilize the context below to understand Pyxel API constraints (indices, ranges, data formats) when generating data.

pyxel_api_asset_context:
- pyxel.images[i].set(x, y, data): List of the image banks (instances of the Image class) (0-2)
- pyxel.blt(x, y, img, u, v, w, h, [colkey], [rotate], [scale]): Copy the region of size (`w`, `h`) from (`u`, `v`) of the image bank `img`(0-2) to (`x`, `y`)
- pyxel.tilemaps[i].set(x, y, data): List of the tilemaps (instances of the Tilemap class) (0-7)
- pyxel.bltm(x, y, tm, u, v, w, h, [colkey], [rotate], [scale]): Copy the region of size (`w`, `h`) from (`u`, `v`) of the tilemap `tm`(0-7) to (`x`, `y`)
- pyxel.sounds[i].set(notes, tones, volumes, effects, speed): List of the sounds (instances of the Sound class) (0-63)
- pyxel.play(ch, snd, [sec], [loop], [resume]): Play the sound `snd`(0-63) on channel `ch`(0-3)
- pyxel.musics[i].set(seq0, seq1, seq2, ...): List of the musics (instances of the Music class) (0-7)
- pyxel.playm(msc, [sec], [loop]): Play the music `msc`(0-7)
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_instruction}"),
        ("human", "{question}"),
    ]
)
model = ChatGoogleGenerativeAI(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-2.5-flash")
structured_model = model.with_structured_output(json_schema, method="json_mode")
chain = prompt | structured_model
output = chain.invoke({"system_instruction": system_instruction, "question": input("Question: ")})

print(json.dumps(output, ensure_ascii=False, indent=2))
