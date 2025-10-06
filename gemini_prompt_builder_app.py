#!/usr/bin/env python3
"""
Gemini 2.5 Flash Image Prompt Generator V4.1
============================================
Enhanced with:
- Professional camera bodies (Canon EOS R5 Mark II, etc.)
- Expanded lens options (35mm, etc.)
- Advanced texture combination system
- Strict realism anchors (no plastic/CGI effects)
"""

import streamlit as st
import random
import re
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Set
from itertools import combinations

# ---------- Optional Ollama Integration -----------------------------------

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# ---------- Configuration -------------------------------------------------

VERSION = "4.1.0"
APP_TITLE = "Gemini 2.5 Flash Image Prompt Generator"
APP_ICON = "📸"

# ---------- Camera Bodies Dictionary --------------------------------------

CAMERA_BODIES = {
    # Canon RF Mount
    "Canon EOS R5 Mark II": {
        "mount": "Canon RF",
        "sensor": "Full-frame 45MP",
        "description": "Professional mirrorless flagship",
        "tier": "flagship",
        "brand": "Canon"
    },
    "Canon EOS R5": {
        "mount": "Canon RF",
        "sensor": "Full-frame 45MP",
        "description": "High-resolution hybrid camera",
        "tier": "professional",
        "brand": "Canon"
    },
    "Canon EOS R6 Mark II": {
        "mount": "Canon RF",
        "sensor": "Full-frame 24MP",
        "description": "Versatile full-frame mirrorless",
        "tier": "professional",
        "brand": "Canon"
    },
    "Canon EOS R3": {
        "mount": "Canon RF",
        "sensor": "Full-frame 24MP stacked",
        "description": "Professional sports camera",
        "tier": "flagship",
        "brand": "Canon"
    },
    
    # Sony E-Mount
    "Sony A1": {
        "mount": "Sony E",
        "sensor": "Full-frame 50MP stacked",
        "description": "Professional flagship mirrorless",
        "tier": "flagship",
        "brand": "Sony"
    },
    "Sony A7R V": {
        "mount": "Sony E",
        "sensor": "Full-frame 61MP",
        "description": "High-resolution specialist",
        "tier": "professional",
        "brand": "Sony"
    },
    "Sony A7 IV": {
        "mount": "Sony E",
        "sensor": "Full-frame 33MP",
        "description": "Versatile hybrid camera",
        "tier": "prosumer",
        "brand": "Sony"
    },
    
    # Nikon Z-Mount
    "Nikon Z9": {
        "mount": "Nikon Z",
        "sensor": "Full-frame 45MP stacked",
        "description": "Professional flagship",
        "tier": "flagship",
        "brand": "Nikon"
    },
    "Nikon Z8": {
        "mount": "Nikon Z",
        "sensor": "Full-frame 45MP stacked",
        "description": "Compact professional body",
        "tier": "professional",
        "brand": "Nikon"
    },
    
    # Fujifilm X-Mount
    "Fujifilm X-H2S": {
        "mount": "Fujifilm X",
        "sensor": "APS-C 26MP stacked",
        "description": "Professional sports camera",
        "tier": "professional",
        "brand": "Fujifilm"
    },
    "Fujifilm GFX 100 II": {
        "mount": "Fujifilm G",
        "sensor": "Medium format 102MP",
        "description": "Medium format powerhouse",
        "tier": "flagship",
        "brand": "Fujifilm"
    },
    
    # Leica
    "Leica SL3": {
        "mount": "Leica L",
        "sensor": "Full-frame 60MP",
        "description": "Premium professional camera",
        "tier": "flagship",
        "brand": "Leica"
    },
    
    # Hasselblad
    "Hasselblad X2D 100C": {
        "mount": "Hasselblad X",
        "sensor": "Medium format 100MP",
        "description": "Ultimate medium format",
        "tier": "flagship",
        "brand": "Hasselblad"
    },
}

# ---------- Lens Configurations -------------------------------------------

LENS_LIBRARY = {
    # Wide-angle lenses
    "16mm f/2.8": {
        "focal_length": 16,
        "max_aperture": 2.8,
        "type": "ultra-wide",
        "description": "ultra-wide 16mm f/2.8 lens for dramatic environmental perspective",
        "use_case": ["landscape", "architecture", "environmental"],
        "characteristics": "extreme field of view with minimal distortion"
    },
    "24mm f/1.4": {
        "focal_length": 24,
        "max_aperture": 1.4,
        "type": "wide",
        "description": "wide-angle 24mm f/1.4 lens with excellent low-light capability",
        "use_case": ["landscape", "environmental", "astrophotography"],
        "characteristics": "sharp across the frame with beautiful bokeh"
    },
    "24mm f/2.8": {
        "focal_length": 24,
        "max_aperture": 2.8,
        "type": "wide",
        "description": "compact 24mm f/2.8 wide-angle lens",
        "use_case": ["landscape", "street", "documentary"],
        "characteristics": "lightweight and portable with good sharpness"
    },
    "35mm f/1.4": {
        "focal_length": 35,
        "max_aperture": 1.4,
        "type": "wide-normal",
        "description": "versatile 35mm f/1.4 lens with natural perspective",
        "use_case": ["street", "documentary", "portrait", "environmental"],
        "characteristics": "excellent for storytelling with shallow depth of field"
    },
    "35mm f/1.8": {
        "focal_length": 35,
        "max_aperture": 1.8,
        "type": "wide-normal",
        "description": "compact 35mm f/1.8 lens for everyday photography",
        "use_case": ["street", "documentary", "travel"],
        "characteristics": "lightweight with natural field of view"
    },
    "35mm f/2": {
        "focal_length": 35,
        "max_aperture": 2.0,
        "type": "wide-normal",
        "description": "35mm f/2 lens balancing size and performance",
        "use_case": ["street", "travel", "general"],
        "characteristics": "compact and sharp with pleasant rendering"
    },
    
    # Standard lenses
    "50mm f/1.2": {
        "focal_length": 50,
        "max_aperture": 1.2,
        "type": "standard",
        "description": "premium 50mm f/1.2 lens with ultra-shallow depth of field",
        "use_case": ["portrait", "low-light", "artistic"],
        "characteristics": "exceptional bokeh and subject isolation"
    },
    "50mm f/1.4": {
        "focal_length": 50,
        "max_aperture": 1.4,
        "type": "standard",
        "description": "classic 50mm f/1.4 standard lens with natural perspective",
        "use_case": ["portrait", "street", "general"],
        "characteristics": "versatile focal length with excellent low-light performance"
    },
    "50mm f/1.8": {
        "focal_length": 50,
        "max_aperture": 1.8,
        "type": "standard",
        "description": "affordable 50mm f/1.8 standard lens",
        "use_case": ["portrait", "general", "beginner"],
        "characteristics": "sharp and lightweight at all apertures"
    },
    
    # Portrait lenses
    "85mm f/1.2": {
        "focal_length": 85,
        "max_aperture": 1.2,
        "type": "portrait",
        "description": "premium 85mm f/1.2 portrait lens with legendary bokeh",
        "use_case": ["portrait", "fashion", "fine-art"],
        "characteristics": "creamy bokeh and exceptional subject separation"
    },
    "85mm f/1.4": {
        "focal_length": 85,
        "max_aperture": 1.4,
        "type": "portrait",
        "description": "professional 85mm f/1.4 portrait lens",
        "use_case": ["portrait", "wedding", "editorial"],
        "characteristics": "beautiful compression and smooth out-of-focus rendering"
    },
    "85mm f/1.8": {
        "focal_length": 85,
        "max_aperture": 1.8,
        "type": "portrait",
        "description": "compact 85mm f/1.8 portrait lens",
        "use_case": ["portrait", "event", "street"],
        "characteristics": "sharp with pleasant bokeh at accessible price"
    },
    "105mm f/1.4": {
        "focal_length": 105,
        "max_aperture": 1.4,
        "type": "portrait-tele",
        "description": "unique 105mm f/1.4 portrait lens with extreme bokeh",
        "use_case": ["portrait", "artistic", "fashion"],
        "characteristics": "exceptional subject isolation and dreamy bokeh"
    },
    
    # Telephoto portrait
    "135mm f/1.8": {
        "focal_length": 135,
        "max_aperture": 1.8,
        "type": "telephoto-portrait",
        "description": "telephoto 135mm f/1.8 lens with strong compression",
        "use_case": ["portrait", "fashion", "sports"],
        "characteristics": "strong perspective compression and ultra-shallow DOF"
    },
    "135mm f/2": {
        "focal_length": 135,
        "max_aperture": 2.0,
        "type": "telephoto-portrait",
        "description": "classic 135mm f/2 telephoto portrait lens",
        "use_case": ["portrait", "wedding", "sports"],
        "characteristics": "flattering compression with smooth bokeh"
    },
    
    # Macro lenses
    "90mm f/2.8 Macro": {
        "focal_length": 90,
        "max_aperture": 2.8,
        "type": "macro",
        "description": "90mm f/2.8 1:1 macro lens for extreme detail",
        "use_case": ["macro", "product", "portrait"],
        "characteristics": "1:1 magnification with exceptional sharpness"
    },
    "100mm f/2.8 Macro": {
        "focal_length": 100,
        "max_aperture": 2.8,
        "type": "macro",
        "description": "100mm f/2.8 1:1 macro lens with image stabilization",
        "use_case": ["macro", "product", "nature"],
        "characteristics": "true 1:1 reproduction with superb micro-contrast"
    },
    
    # Telephoto lenses
    "200mm f/2": {
        "focal_length": 200,
        "max_aperture": 2.0,
        "type": "telephoto",
        "description": "professional 200mm f/2 telephoto lens",
        "use_case": ["sports", "wildlife", "portrait"],
        "characteristics": "extreme compression and background isolation"
    },
    "70-200mm f/2.8": {
        "focal_length": "70-200",
        "max_aperture": 2.8,
        "type": "telephoto-zoom",
        "description": "professional 70-200mm f/2.8 zoom lens",
        "use_case": ["portrait", "wedding", "sports", "event"],
        "characteristics": "versatile range with constant f/2.8 aperture"
    },
}

# ---------- Texture System with Combinations ------------------------------

class TextureManager:
    """Advanced texture handling with combination support."""
    
    TEXTURE_LIBRARY = {
        # Human/Organic
        "skin_realistic": {
            "description": "natural skin texture with visible pores, fine lines, and individual hair strands",
            "category": "organic",
            "intensity": "high",
            "compatible_with": ["fabric_detailed", "environmental_rich"]
        },
        "skin_pores": {
            "description": "visible skin pores and natural skin texture detail",
            "category": "organic",
            "intensity": "medium",
            "compatible_with": ["skin_realistic", "fabric_detailed"]
        },
        "hair_strands": {
            "description": "individual hair strands with natural flyaways and texture",
            "category": "organic",
            "intensity": "high",
            "compatible_with": ["skin_realistic", "fabric_detailed"]
        },
        
        # Fabric/Material
        "fabric_detailed": {
            "description": "realistic fabric weave, natural folds, and authentic material reflectance",
            "category": "material",
            "intensity": "high",
            "compatible_with": ["skin_realistic", "environmental_rich"]
        },
        "fabric_weave": {
            "description": "visible fabric weave patterns and textile structure",
            "category": "material",
            "intensity": "medium",
            "compatible_with": ["fabric_detailed", "sharp_micro"]
        },
        "material_reflectance": {
            "description": "accurate material reflectance and surface properties",
            "category": "material",
            "intensity": "medium",
            "compatible_with": ["fabric_detailed", "environmental_rich"]
        },
        
        # Environmental
        "environmental_rich": {
            "description": "atmospheric depth with fine surface details and accurate material properties",
            "category": "environment",
            "intensity": "high",
            "compatible_with": ["skin_realistic", "fabric_detailed", "weathered_aged"]
        },
        "atmospheric_depth": {
            "description": "atmospheric haze and depth perception with distance falloff",
            "category": "environment",
            "intensity": "medium",
            "compatible_with": ["environmental_rich", "sharp_micro"]
        },
        "dust_particles": {
            "description": "visible dust particles and air particulates in lighting",
            "category": "environment",
            "intensity": "low",
            "compatible_with": ["environmental_rich", "atmospheric_depth"]
        },
        
        # Technical
        "sharp_micro": {
            "description": "crisp high-frequency texture detail from foreground to background",
            "category": "technical",
            "intensity": "high",
            "compatible_with": ["fabric_weave", "weathered_aged", "macro_detail"]
        },
        "macro_detail": {
            "description": "extreme close-up detail with microscopic surface features",
            "category": "technical",
            "intensity": "very_high",
            "compatible_with": ["sharp_micro", "material_reflectance"]
        },
        
        # Aging/Weathering
        "weathered_aged": {
            "description": "aged surfaces with wear patterns and patina of time",
            "category": "aging",
            "intensity": "medium",
            "compatible_with": ["environmental_rich", "sharp_micro"]
        },
        "wear_patterns": {
            "description": "natural wear patterns and use marks on surfaces",
            "category": "aging",
            "intensity": "medium",
            "compatible_with": ["weathered_aged", "environmental_rich"]
        },
        
        # Realism anchors (anti-CGI)
        "natural_imperfections": {
            "description": "authentic natural imperfections and organic irregularities",
            "category": "realism",
            "intensity": "medium",
            "compatible_with": ["skin_realistic", "weathered_aged"]
        },
        "unretouched_authentic": {
            "description": "unretouched authentic appearance without digital smoothing",
            "category": "realism",
            "intensity": "high",
            "compatible_with": ["skin_realistic", "natural_imperfections"]
        },
    }
    
    @staticmethod
    def get_all_textures() -> Dict:
        """Get all available textures."""
        return TextureManager.TEXTURE_LIBRARY
    
    @staticmethod
    def get_texture_by_category(category: str) -> Dict:
        """Get textures filtered by category."""
        return {
            k: v for k, v in TextureManager.TEXTURE_LIBRARY.items()
            if v["category"] == category
        }
    
    @staticmethod
    def get_compatible_textures(texture_key: str) -> List[str]:
        """Get list of textures compatible with given texture."""
        if texture_key not in TextureManager.TEXTURE_LIBRARY:
            return []
        return TextureManager.TEXTURE_LIBRARY[texture_key].get("compatible_with", [])
    
    @staticmethod
    def combine_textures(primary: str, secondary: str = None) -> str:
        """
        Combine two textures into a coherent description.
        
        Args:
            primary: Primary texture key
            secondary: Optional secondary texture key
            
        Returns:
            Combined texture description
        """
        if primary not in TextureManager.TEXTURE_LIBRARY:
            return "realistic natural texture detail"
        
        primary_desc = TextureManager.TEXTURE_LIBRARY[primary]["description"]
        
        if not secondary or secondary not in TextureManager.TEXTURE_LIBRARY:
            return primary_desc
        
        # Check compatibility
        compatible = TextureManager.get_compatible_textures(primary)
        if secondary not in compatible:
            # If not compatible, just use primary
            return primary_desc
        
        secondary_desc = TextureManager.TEXTURE_LIBRARY[secondary]["description"]
        
        # Intelligent combination based on categories
        primary_cat = TextureManager.TEXTURE_LIBRARY[primary]["category"]
        secondary_cat = TextureManager.TEXTURE_LIBRARY[secondary]["category"]
        
        if primary_cat == secondary_cat:
            # Same category - combine with "and"
            return f"{primary_desc}, additionally {secondary_desc}"
        else:
            # Different categories - combine with "with"
            return f"{primary_desc}, complemented by {secondary_desc}"
    
    @staticmethod
    def get_all_textures_combined() -> str:
        """Generate ultra-detailed texture description using all compatible elements."""
        categories = {}
        for key, value in TextureManager.TEXTURE_LIBRARY.items():
            cat = value["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(value["description"])
        
        parts = []
        for cat, descs in categories.items():
            if cat == "realism":
                # Realism anchors go at the end
                continue
            parts.extend(descs[:2])  # Take top 2 from each category
        
        # Add realism anchors
        if "realism" in categories:
            parts.extend(categories["realism"])
        
        return ", ".join(parts)


# ---------- Realism Enhancement System ------------------------------------

REALISM_ANCHORS = {
    "standard": (
        "This should look like an authentic photograph taken with a professional DSLR camera, "
        "with natural lighting physics, realistic material properties, and lifelike detail."
    ),
    "strict_no_cgi": (
        "Render as authentic photography with zero CGI, plastic, or airbrushed effects. "
        "Maintain natural skin texture, visible pores, real fabric weave, and organic imperfections. "
        "Avoid any artificial smoothing, digital retouching, or computer-generated appearance. "
        "This must look like it was captured with a real camera sensor."
    ),
    "natural_unretouched": (
        "Completely natural and unretouched photography with authentic textures. "
        "No digital smoothing, no plastic skin, no airbrushing, no CGI elements. "
        "Real camera optics, natural lighting physics, genuine material properties."
    ),
    "photojournalism": (
        "Documentary-style authentic photography with journalistic integrity. "
        "No manipulation, no artificial enhancement, true-to-life representation "
        "with all natural imperfections and organic characteristics preserved."
    )
}

# ---------- Lighting Dictionary -------------------------------------------

LIGHTING = {
    "Soft Natural": "soft, warm natural daylight streaming through a nearby window, creating gentle shadows with a natural falloff",
    "Golden Hour": "golden hour sunlight bathing the scene in warm amber tones with soft ambient bounce light",
    "Studio Professional": "professional three-point studio lighting with soft key light, subtle fill, and rim lighting for depth",
    "Dramatic Side": "high-contrast dramatic lighting from the side, casting deep, moody shadows",
    "Overcast Diffused": "evenly diffused daylight from an overcast sky, eliminating harsh shadows",
    "Backlit Atmospheric": "strong backlighting creating a glowing rim around the subject with atmospheric depth",
    "Night Urban": "neon lights in blues and pinks reflecting off surfaces, creating a moody urban atmosphere",
    "Window Side": "soft window light from the side, creating dimensional modeling with gentle shadows",
    "Rembrandt": "classic Rembrandt lighting with triangular highlight on shadow-side cheek",
    "Butterfly": "butterfly lighting from above creating symmetrical shadow under nose",
}

# ---------- Other Dictionaries (Simplified) -------------------------------

COMPOSITION = {
    "Rule of Thirds": "composed using the rule of thirds, with the main subject positioned off-center for dynamic visual interest",
    "Centered Symmetrical": "framed with perfect symmetry, the subject centered for balance and powerful impact",
    "Leading Lines": "incorporating strong leading lines that naturally guide the viewer's eye toward the main subject",
    "Negative Space": "utilizing generous negative space around the subject for a minimalist, focused composition",
    "Environmental Context": "placing the subject within their environment, showing context and telling a broader visual story",
    "Dutch Angle": "shot with a tilted Dutch angle for dramatic tension",
    "Frame in Frame": "using natural framing elements within the composition",
}

QUALITY = {
    "Photorealistic 8K": "ultra-realistic with physically-based rendering, accurate global illumination, and 8K detail",
    "Film Analog - Portra 400": "shot on Kodak Portra 400 film stock, featuring subtle organic grain and natural color response",
    "Film Analog - Tri-X 400": "captured on Kodak Tri-X 400 black and white film with classic grain structure",
    "Editorial Commercial": "high-end editorial quality with precise color grading and commercial-grade polish",
    "Raw DSLR": "unprocessed DSLR aesthetic with natural dynamic range and authentic sensor characteristics",
    "Large Format Film": "captured on large format 4x5 film with exceptional detail and tonal range",
}

COLOR = {
    "Neutral Accurate": "with neutral, true-to-life color tones maintaining accurate color reproduction",
    "Warm Golden": "with a warm color grade emphasizing golden and amber tones throughout",
    "Cool Cinematic": "with cool cinematic color temperature featuring blue and teal hues",
    "Muted Earthy": "with a desaturated, muted palette of subtle earth tones",
    "Vibrant Saturated": "with enhanced saturation for punchy, vivid colors while maintaining photorealistic quality",
    "Monochrome B&W": "rendered in rich black and white with deep shadows and bright highlights",
}

MOOD = {
    "Serene Peaceful": "The overall mood is serene and calm, creating a peaceful, contemplative atmosphere",
    "Confident Powerful": "The atmosphere conveys strength and self-assurance with subtle but commanding intensity",
    "Intimate Warm": "Creating an intimate, warm emotional connection with soft, inviting energy",
    "Mysterious Dramatic": "Establishing a mysterious, dramatic atmosphere with rich shadows and intrigue",
    "Energetic Dynamic": "Capturing dynamic energy with a sense of vibrant motion and vitality",
    "Contemplative Quiet": "Evoking a thoughtful, introspective quiet moment of reflection",
}

ASPECT_RATIO = {
    "Standard (3:2)": "3:2",
    "Square (1:1)": "1:1",
    "Portrait (2:3)": "2:3",
    "Widescreen (16:9)": "16:9",
    "Portrait Wide (9:16)": "9:16",
    "Cinema (2.39:1)": "2.39:1",
}

# ---------- Preset Templates ----------------------------------------------

PRESETS = {
    "Portrait - Studio Canon R5": {
        "mode": "Portrait",
        "subject": "professional model with natural expression",
        "setting": "clean studio environment",
        "camera_body": "Canon EOS R5 Mark II",
        "lens": "85mm f/1.4",
        "lighting": "Studio Professional",
        "composition": "Rule of Thirds",
        "texture_primary": "skin_realistic",
        "texture_secondary": "fabric_detailed",
        "quality": "Photorealistic 8K",
        "color": "Neutral Accurate",
        "mood": "Confident Powerful",
        "realism_mode": "strict_no_cgi",
    },
    "Editorial - Fashion Sony A1": {
        "mode": "Editorial",
        "subject": "fashion model in designer clothing",
        "setting": "minimalist urban backdrop",
        "camera_body": "Sony A1",
        "lens": "135mm f/1.8",
        "lighting": "Dramatic Side",
        "composition": "Negative Space",
        "texture_primary": "fabric_detailed",
        "texture_secondary": "skin_realistic",
        "quality": "Editorial Commercial",
        "color": "Cool Cinematic",
        "mood": "Confident Powerful",
        "realism_mode": "natural_unretouched",
    },
    "Portrait - Natural 35mm": {
        "mode": "Portrait",
        "subject": "candid portrait with authentic expression",
        "setting": "natural indoor environment near window",
        "camera_body": "Canon EOS R6 Mark II",
        "lens": "35mm f/1.4",
        "lighting": "Window Side",
        "composition": "Environmental Context",
        "texture_primary": "skin_realistic",
        "texture_secondary": "natural_imperfections",
        "quality": "Raw DSLR",
        "color": "Warm Golden",
        "mood": "Intimate Warm",
        "realism_mode": "photojournalism",
    },
    "Product - Macro Detail": {
        "mode": "Product",
        "subject": "artisan product with intricate details",
        "setting": "neutral backdrop with subtle gradient",
        "camera_body": "Fujifilm GFX 100 II",
        "lens": "100mm f/2.8 Macro",
        "lighting": "Studio Professional",
        "composition": "Centered Symmetrical",
        "texture_primary": "macro_detail",
        "texture_secondary": "sharp_micro",
        "quality": "Photorealistic 8K",
        "color": "Neutral Accurate",
        "mood": "Serene Peaceful",
        "realism_mode": "standard",
    },
}

# ---------- Utility Functions ---------------------------------------------

def sanitize_text(text: str) -> str:
    """Remove problematic characters and limit length."""
    clean = re.sub(r'[\";<>]', '', text)
    return clean[:500].strip()


def grammar_cleanup(text: str) -> str:
    """Fix spacing and punctuation."""
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', text)
    return text.strip()


def validate_input(text: str, min_length: int = 3) -> bool:
    """Validate user input."""
    return bool(text and len(text.strip()) >= min_length)


def build_camera_description(camera_body: str, lens: str, iso: int = 100) -> str:
    """
    Build complete camera description with body + lens.
    
    Args:
        camera_body: Camera body name
        lens: Lens specification
        iso: ISO value
        
    Returns:
        Complete camera description string
    """
    camera_info = CAMERA_BODIES.get(camera_body, {})
    lens_info = LENS_LIBRARY.get(lens, {})
    
    if not lens_info:
        # Fallback for custom lens
        lens_desc = f"using a {lens} lens at ISO {iso}"
    else:
        lens_desc = lens_info["description"]
        characteristics = lens_info.get("characteristics", "")
        lens_desc = f"using a {lens_desc} at ISO {iso}, {characteristics}"
    
    if camera_info:
        sensor = camera_info.get("sensor", "professional sensor")
        return f"captured on a {camera_body} ({sensor}) {lens_desc}"
    else:
        return f"captured {lens_desc}"


# ---------- Prompt Builder ------------------------------------------------

def build_prompt(
    mode: str,
    subject: str,
    setting: str,
    camera_body: str,
    lens: str,
    iso: int,
    lighting: str,
    composition: str,
    texture_primary: str,
    texture_secondary: Optional[str],
    texture_mode: str,
    quality: str,
    mood: str,
    color: str,
    aspect_ratio: str,
    realism_mode: str,
    negative: str = "",
    randomize: bool = False,
) -> Dict:
    """Build enhanced photographic prompt with advanced texture handling."""
    
    # Sanitize inputs
    subject = sanitize_text(subject)
    setting = sanitize_text(setting)
    
    # Handle randomization
    if randomize:
        lighting = random.choice(list(LIGHTING.keys()))
        mood = random.choice(list(MOOD.keys()))
        color = random.choice(list(COLOR.keys()))
        lens = random.choice(list(LENS_LIBRARY.keys()))
    
    # Get values
    ratio = ASPECT_RATIO[aspect_ratio]
    
    # Build camera description
    camera_desc = build_camera_description(camera_body, lens, iso)
    
    # Build texture description based on mode
    texture_manager = TextureManager()
    
    if texture_mode == "all_combined":
        texture_desc = texture_manager.get_all_textures_combined()
    elif texture_mode == "primary_secondary" and texture_secondary:
        texture_desc = texture_manager.combine_textures(texture_primary, texture_secondary)
    else:
        texture_desc = texture_manager.combine_textures(texture_primary)
    
    # Build prompt parts
    prompt_parts = []
    
    # Opening
    prompt_parts.append(f"A photorealistic {mode.lower()} photograph of {subject}, set in {setting}.")
    
    # Lighting
    prompt_parts.append(f"The scene is illuminated by {LIGHTING[lighting]}.")
    
    # Camera and composition
    prompt_parts.append(f"The image is {camera_desc}, {COMPOSITION[composition]}.")
    
    # Quality and texture
    prompt_parts.append(f"The photograph is {QUALITY[quality]}, {texture_desc}.")
    
    # Mood and color
    mood_text = MOOD[mood].rstrip('.')
    color_text = COLOR[color]
    prompt_parts.append(f"{mood_text} {color_text}.")
    
   # Aspect ratio
    prompt_parts.append(f"Image format: {ratio} aspect ratio.")
    
    # Combine base prompt
    base_prompt = " ".join(prompt_parts)
    base_prompt = grammar_cleanup(base_prompt)
    
    # Append realism anchor based on mode
    realism_anchor = REALISM_ANCHORS.get(realism_mode, REALISM_ANCHORS["standard"])
    final_prompt = f"{base_prompt} {realism_anchor}"
    final_prompt = grammar_cleanup(final_prompt)
    
    # Add negative prompt with anti-CGI defaults
    default_negatives = [
        "plastic skin", "airbrushed", "CGI", "3D render", "digital painting",
        "artificial smoothing", "unrealistic textures", "synthetic appearance",
        "overly smooth skin", "fake materials"
    ]
    
    if negative and negative.strip():
        sanitized_negative = sanitize_text(negative)
        combined_negative = f"{sanitized_negative}, {', '.join(default_negatives)}"
    else:
        combined_negative = ", ".join(default_negatives)
    
    final_prompt += f"\n\nAvoid: {combined_negative}"
    
    # Metadata
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "version": VERSION,
        "mode": mode,
        "camera_body": camera_body,
        "lens": lens,
        "iso": iso,
        "lighting": lighting,
        "composition": composition,
        "texture_primary": texture_primary,
        "texture_secondary": texture_secondary,
        "texture_mode": texture_mode,
        "quality": quality,
        "mood": mood,
        "color": color,
        "aspect_ratio": ratio,
        "realism_mode": realism_mode,
        "randomized": randomize,
    }
    
    return {
        "prompt": final_prompt,
        "metadata": metadata,
    }


# ---------- Ollama Integration (Simplified) -------------------------------

def get_available_models() -> List[str]:
    """Get list of available Ollama models."""
    if not OLLAMA_AVAILABLE:
        return []
    
    try:
        models = ollama.list()
        return sorted([m['name'] for m in models.get('models', [])])
    except Exception:
        return []


# ---------- Streamlit Application -----------------------------------------

def main():
    """Main Streamlit application."""
    
    # Page config
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            background-color: #FF4B4B;
            color: white;
            height: 3em;
            border-radius: 8px;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #FF6B6B;
        }
        .camera-badge {
            display: inline-block;
            padding: 0.3em 0.8em;
            border-radius: 6px;
            font-size: 0.85em;
            font-weight: 600;
            margin: 0.2em;
        }
        .flagship { background-color: #6f42c1; color: white; }
        .professional { background-color: #007bff; color: white; }
        .prosumer { background-color: #17a2b8; color: white; }
        .texture-info {
            background-color: #f8f9fa;
            padding: 1em;
            border-radius: 8px;
            border-left: 4px solid #007bff;
            margin: 1em 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'prompt_history' not in st.session_state:
        st.session_state.prompt_history = []
    
    # Header
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.markdown(f"""
    **Version {VERSION}** - Enhanced Edition
    - 🎥 Professional Camera Bodies (Canon R5 Mark II, Sony A1, etc.)
    - 🔍 Expanded Lens Library (35mm, 85mm, 135mm, Macro, etc.)
    - 🎨 Advanced Texture Combination System
    - ✨ Strict Realism (No Plastic/CGI/Airbrushing)
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Realism mode selector
        st.subheader("🎯 Realism Mode")
        realism_mode = st.selectbox(
            "Anti-CGI Protection",
            list(REALISM_ANCHORS.keys()),
            index=1,  # Default to strict_no_cgi
            help="Control level of realism enforcement"
        )
        
        realism_descriptions = {
            "standard": "Basic photorealistic rendering",
            "strict_no_cgi": "⭐ Recommended - Strictly prevents CGI/plastic effects",
            "natural_unretouched": "Emphasis on unretouched authenticity",
            "photojournalism": "Documentary-style integrity"
        }
        
        st.caption(realism_descriptions.get(realism_mode, ""))
        
        st.divider()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        randomize = st.toggle(
            "🎲 Randomize",
            value=False,
            help="Randomly select lighting, mood, color, and lens"
        )
        
        show_texture_info = st.toggle(
            "📊 Show Texture Details",
            value=False,
            help="Display texture compatibility information"
        )
        
        if st.button("🔄 Clear All", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        
        st.divider()
        
        # Camera database info
        st.subheader("📷 Camera Database")
        st.caption(f"Bodies: {len(CAMERA_BODIES)}")
        st.caption(f"Lenses: {len(LENS_LIBRARY)}")
        st.caption(f"Textures: {len(TextureManager.TEXTURE_LIBRARY)}")
        
        with st.expander("📖 View Camera Bodies"):
            for brand in set(c['brand'] for c in CAMERA_BODIES.values()):
                st.markdown(f"**{brand}**")
                brand_cameras = [k for k, v in CAMERA_BODIES.items() if v['brand'] == brand]
                for cam in brand_cameras[:3]:  # Show first 3
                    tier = CAMERA_BODIES[cam]['tier']
                    st.caption(f"• {cam} ({tier})")
        
        with st.expander("🔍 View Lens Library"):
            lens_types = {}
            for lens, info in LENS_LIBRARY.items():
                lens_type = info['type']
                if lens_type not in lens_types:
                    lens_types[lens_type] = []
                lens_types[lens_type].append(lens)
            
            for lens_type, lenses in sorted(lens_types.items()):
                st.markdown(f"**{lens_type.replace('-', ' ').title()}**")
                for lens in lenses[:3]:
                    st.caption(f"• {lens}")
        
        # Resources
        with st.expander("📚 Resources"):
            st.markdown("""
            - [Gemini API Docs](https://ai.google.dev/gemini-api/docs/image-generation)
            - [Camera Database](https://www.dpreview.com/)
            - [Lens Guide](https://www.the-digital-picture.com/)
            """)
    
    # Main content
    st.divider()
    
    # Preset buttons
    st.subheader("🎯 Quick Start Presets")
    preset_cols = st.columns(len(PRESETS))
    
    for idx, (preset_name, preset_data) in enumerate(PRESETS.items()):
        with preset_cols[idx]:
            if st.button(preset_name, use_container_width=True, key=f"preset_{idx}"):
                for key, value in preset_data.items():
                    st.session_state[f"input_{key}"] = value
                st.success(f"✅ Loaded: {preset_name}")
                st.rerun()
    
    st.divider()
    
    # Input form with tabs for better organization
    tab1, tab2, tab3 = st.tabs(["📝 Basic Settings", "📷 Camera & Lens", "🎨 Advanced Settings"])
    
    # TAB 1: Basic Settings
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            mode = st.selectbox(
                "Photography Mode",
                ["Portrait", "Landscape", "Editorial", "Product", "Documentary"],
                key="input_mode"
            )
            
            subject = st.text_area(
                "Subject Description ✱",
                value=st.session_state.get("input_subject", ""),
                height=100,
                placeholder="e.g., professional fashion model in elegant evening gown",
                help="Describe who or what is in the photograph",
                key="subject_input"
            )
        
        with col2:
            aspect_ratio = st.selectbox(
                "Aspect Ratio",
                list(ASPECT_RATIO.keys()),
                key="input_aspect_ratio"
            )
            
            setting = st.text_area(
                "Setting/Environment ✱",
                value=st.session_state.get("input_setting", ""),
                height=100,
                placeholder="e.g., minimalist studio with soft gradient backdrop",
                help="Describe where the photograph takes place",
                key="setting_input"
            )
    
    # TAB 2: Camera & Lens
    with tab2:
        st.markdown("### 📷 Camera Body Selection")
        
        # Group cameras by brand
        camera_brands = {}
        for camera, info in CAMERA_BODIES.items():
            brand = info['brand']
            if brand not in camera_brands:
                camera_brands[brand] = []
            camera_brands[brand].append(camera)
        
        col1, col2 = st.columns(2)
        
        with col1:
            camera_brand = st.selectbox(
                "Camera Brand",
                sorted(camera_brands.keys()),
                help="Select camera manufacturer"
            )
            
            camera_body = st.selectbox(
                "Camera Body",
                camera_brands[camera_brand],
                key="input_camera_body",
                help="Professional camera bodies"
            )
            
            # Display camera info
            if camera_body in CAMERA_BODIES:
                cam_info = CAMERA_BODIES[camera_body]
                tier_class = cam_info['tier']
                st.markdown(
                    f'<span class="camera-badge {tier_class}">{tier_class.upper()}</span>',
                    unsafe_allow_html=True
                )
                st.caption(f"📊 {cam_info['sensor']}")
                st.caption(f"🔧 {cam_info['mount']} mount")
        
        with col2:
            # Group lenses by type
            lens_types = {}
            for lens, info in LENS_LIBRARY.items():
                lens_type = info['type']
                if lens_type not in lens_types:
                    lens_types[lens_type] = []
                lens_types[lens_type].append(lens)
            
            lens_type_filter = st.selectbox(
                "Lens Type",
                sorted(lens_types.keys()),
                format_func=lambda x: x.replace("-", " ").title(),
                help="Filter lenses by type"
            )
            
            lens = st.selectbox(
                "Lens",
                lens_types[lens_type_filter],
                key="input_lens",
                help="Professional lens selection"
            )
            
            # Display lens info
            if lens in LENS_LIBRARY:
                lens_info = LENS_LIBRARY[lens]
                st.caption(f"📐 Focal: {lens_info['focal_length']}mm")
                st.caption(f"🔆 Max aperture: f/{lens_info['max_aperture']}")
                st.caption(f"💡 {lens_info['characteristics']}")
        
        # ISO setting
        st.markdown("### ⚙️ ISO Setting")
        iso = st.select_slider(
            "ISO Sensitivity",
            options=[50, 100, 200, 400, 800, 1600, 3200, 6400],
            value=100,
            help="Camera sensor sensitivity"
        )
    
    # TAB 3: Advanced Settings
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💡 Lighting & Atmosphere")
            
            lighting = st.selectbox(
                "Lighting Setup",
                list(LIGHTING.keys()),
                key="input_lighting"
            )
            
            mood = st.selectbox(
                "Mood/Atmosphere",
                list(MOOD.keys()),
                key="input_mood"
            )
            
            color = st.selectbox(
                "Color Treatment",
                list(COLOR.keys()),
                key="input_color"
            )
            
            composition = st.selectbox(
                "Composition Style",
                list(COMPOSITION.keys()),
                key="input_composition"
            )
        
        with col2:
            st.markdown("### 🎨 Texture System")
            
            texture_mode = st.radio(
                "Texture Mode",
                ["single", "primary_secondary", "all_combined"],
                format_func=lambda x: {
                    "single": "Single Texture",
                    "primary_secondary": "Primary + Secondary (Recommended)",
                    "all_combined": "All Textures Combined (Ultra Detail)"
                }[x],
                help="Choose texture complexity level"
            )
            
            texture_manager = TextureManager()
            all_textures = list(texture_manager.get_all_textures().keys())
            
            texture_primary = st.selectbox(
                "Primary Texture",
                all_textures,
                index=all_textures.index("skin_realistic") if "skin_realistic" in all_textures else 0,
                key="input_texture_primary",
                help="Main texture focus"
            )
            
            if texture_mode == "primary_secondary":
                # Get compatible textures
                compatible = texture_manager.get_compatible_textures(texture_primary)
                
                if compatible:
                    texture_secondary = st.selectbox(
                        "Secondary Texture (Compatible)",
                        [None] + compatible,
                        key="input_texture_secondary",
                        help="Additional compatible texture"
                    )
                else:
                    st.warning("No compatible secondary textures available")
                    texture_secondary = None
            else:
                texture_secondary = None
            
            quality = st.selectbox(
                "Quality/Rendering",
                list(QUALITY.keys()),
                key="input_quality"
            )
        
        # Texture info display
        if show_texture_info:
            st.markdown("### 📊 Texture Information")
            
            texture_info = texture_manager.TEXTURE_LIBRARY[texture_primary]
            
            st.markdown(f"""
            <div class="texture-info">
                <strong>{texture_primary.replace('_', ' ').title()}</strong><br>
                <em>Category:</em> {texture_info['category']}<br>
                <em>Intensity:</em> {texture_info['intensity']}<br>
                <em>Description:</em> {texture_info['description']}
            </div>
            """, unsafe_allow_html=True)
            
            if texture_secondary:
                secondary_info = texture_manager.TEXTURE_LIBRARY[texture_secondary]
                st.markdown(f"""
                <div class="texture-info">
                    <strong>{texture_secondary.replace('_', ' ').title()}</strong><br>
                    <em>Category:</em> {secondary_info['category']}<br>
                    <em>Intensity:</em> {secondary_info['intensity']}<br>
                    <em>Description:</em> {secondary_info['description']}
                </div>
                """, unsafe_allow_html=True)
    
    # Negative prompt (below tabs)
    st.divider()
    
    with st.expander("🚫 Negative Prompt (Advanced)", expanded=False):
        st.info("💡 Default anti-CGI negatives are automatically included")
        negative = st.text_area(
            "Additional Elements to Avoid",
            value=st.session_state.get("input_negative", ""),
            placeholder="e.g., motion blur, overexposure, lens flare",
            help="Additional elements to exclude (CGI/plastic prevention is automatic)",
            height=80
        )
        
        st.caption("**Automatically excluded:** plastic skin, airbrushed, CGI, 3D render, artificial smoothing, etc.")
    
    st.divider()
    
    # Generate button
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        generate_button = st.button(
            "✨ Generate Prompt",
            type="primary",
            use_container_width=True
        )
    
    # Generation logic
    if generate_button:
        # Validation
        if not validate_input(subject):
            st.error("❌ Subject description is required (minimum 3 characters)")
        elif not validate_input(setting):
            st.error("❌ Setting description is required (minimum 3 characters)")
        else:
            # Generate prompt
            with st.spinner("🎨 Crafting your ultra-realistic prompt..."):
                result = build_prompt(
                    mode=mode,
                    subject=subject,
                    setting=setting,
                    camera_body=camera_body,
                    lens=lens,
                    iso=iso,
                    lighting=lighting,
                    composition=composition,
                    texture_primary=texture_primary,
                    texture_secondary=texture_secondary,
                    texture_mode=texture_mode,
                    quality=quality,
                    mood=mood,
                    color=color,
                    aspect_ratio=aspect_ratio,
                    realism_mode=realism_mode,
                    negative=negative,
                    randomize=randomize,
                )
            
            # Save to history
            st.session_state.prompt_history.append(result)
            
            # Display result
            st.success("✅ Prompt generated successfully!")
            
            # Show key features used
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Camera", camera_body.split()[0])
            with col2:
                st.metric("Lens", lens.split()[0])
            with col3:
                st.metric("Texture Mode", texture_mode.replace("_", " ").title())
            with col4:
                st.metric("Realism", realism_mode.split("_")[0].title())
            
            st.divider()
            
            # Prompt output
            st.subheader("📋 Your Generated Prompt")
            
            st.text_area(
                "Copy this prompt:",
                value=result['prompt'],
                height=300,
                key="final_prompt"
            )
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.download_button(
                    label="💾 Download TXT",
                    data=result['prompt'],
                    file_name=f"gemini_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                st.download_button(
                    label="📊 Download JSON",
                    data=json.dumps(result['metadata'], indent=2),
                    file_name=f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col3:
                if st.button("📋 Copy Guide", use_container_width=True):
                    st.code(result['prompt'], language=None)
                    st.caption("👆 Select all and copy (Ctrl+C / Cmd+C)")
            
            with col4:
                if st.button("🔄 Generate Variation", use_container_width=True):
                    st.session_state['randomize_next'] = True
                    st.rerun()
            
            # Technical details
            with st.expander("🔍 View Technical Specifications"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Camera Setup**")
                    st.caption(f"Body: {result['metadata']['camera_body']}")
                    st.caption(f"Lens: {result['metadata']['lens']}")
                    st.caption(f"ISO: {result['metadata']['iso']}")
                    st.caption(f"Composition: {result['metadata']['composition']}")
                
                with col2:
                    st.markdown("**Visual Style**")
                    st.caption(f"Lighting: {result['metadata']['lighting']}")
                    st.caption(f"Quality: {result['metadata']['quality']}")
                    st.caption(f"Mood: {result['metadata']['mood']}")
                    st.caption(f"Color: {result['metadata']['color']}")
                
                with col3:
                    st.markdown("**Texture & Realism**")
                    st.caption(f"Primary: {result['metadata']['texture_primary']}")
                    st.caption(f"Secondary: {result['metadata'].get('texture_secondary', 'None')}")
                    st.caption(f"Mode: {result['metadata']['texture_mode']}")
                    st.caption(f"Realism: {result['metadata']['realism_mode']}")
            
            # Texture breakdown
            if texture_mode == "primary_secondary" and texture_secondary:
                with st.expander("🎨 Texture Combination Preview"):
                    texture_manager = TextureManager()
                    combined = texture_manager.combine_textures(texture_primary, texture_secondary)
                    st.info(f"**Combined Texture Description:**\n\n{combined}")
    
    # Prompt History
    if st.session_state.prompt_history:
        st.divider()
        st.subheader("📚 Recent Prompts")
        
        # Show last 3 prompts
        recent_prompts = st.session_state.prompt_history[-3:][::-1]
        
        for idx, result in enumerate(recent_prompts):
            with st.expander(
                f"Prompt {len(st.session_state.prompt_history) - idx} - "
                f"{result['metadata']['camera_body']} + {result['metadata']['lens']}"
            ):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.text_area(
                        "Prompt",
                        value=result['prompt'],
                        height=150,
                        key=f"history_{idx}",
                        disabled=True
                    )
                
                with col2:
                    st.caption(f"**Camera:** {result['metadata']['camera_body']}")
                    st.caption(f"**Lens:** {result['metadata']['lens']}")
                    st.caption(f"**Texture:** {result['metadata']['texture_mode']}")
                    st.caption(f"**Realism:** {result['metadata']['realism_mode']}")
                
                if st.button(f"🔄 Reuse Settings", key=f"reuse_{idx}"):
                    for key, value in result['metadata'].items():
                        if key not in ['timestamp', 'version', 'randomized']:
                            st.session_state[f"input_{key}"] = value
                    st.success("✅ Settings loaded from history")
                    st.rerun()
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 2em 0;'>
            <p><strong>Gemini 2.5 Flash Image Prompt Generator V4.1</strong></p>
            <p>Enhanced Edition with Professional Camera Bodies & Advanced Texture System</p>
            <p style='font-size: 0.9em;'>
                Following official Gemini guidelines | Anti-CGI/Plastic Protection | 
                {cameras} Camera Bodies | {lenses} Lenses | {textures} Textures
            </p>
        </div>
    """.format(
        cameras=len(CAMERA_BODIES),
        lenses=len(LENS_LIBRARY),
        textures=len(TextureManager.TEXTURE_LIBRARY)
    ), unsafe_allow_html=True)


# ---------- Run Application -----------------------------------------------

if __name__ == "__main__":
    main()