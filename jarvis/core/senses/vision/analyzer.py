import ollama
import os
import re

class VisionAnalyzer:
    """
    Unified Vision Analysis core using LLaVA.
    Replaces legacy moondream implementation.
    """
    def __init__(self, model="llava"):
        self.model = model
        self._initialized = True

    def analyze_image(self, image_path: str, prompt: str = "Describe this image.") -> str:
        """Analyze an image file using LLaVA."""
        if not os.path.exists(image_path):
            return "Error: Image file not found."
            
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                images=[image_path]
            )
            
            res_text = response.get('response', "").strip()
            # Clean think tags
            res_text = re.sub(r'<think>.*?</think>', '', res_text, flags=re.DOTALL).strip()
            return res_text
        except Exception as e:
            return f"Vision Analysis Error: {str(e)}"

    def describe_scene(self, image_path: str) -> str:
        return self.analyze_image(image_path, "Describe the scene and the people in it.")
