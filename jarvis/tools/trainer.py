"""
jarvis/tools/trainer.py
Infrastructure for LoRA Fine-Tuning.
Exports ChromaDB conversations into training datasets.
"""

import json
import os
from jarvis.core.brain.memory import LongTermMemory

class LoRATrainer:
    def __init__(self):
        self.memory = LongTermMemory()
        self.output_dir = "data/training"
        os.makedirs(self.output_dir, exist_ok=True)

    def export_dataset(self, format="alpaca"):
        """Exports memories into a JSONL file for fine-tuning."""
        # Get all documents from conversation history
        # Note: ChromaDB's get() without where filter returns everything in the collection
        data = self.memory.conv_history.get()
        
        documents = data.get('documents', [])
        metadatas = data.get('metadatas', [])
        
        training_set = []
        
        for doc in documents:
            try:
                # Our storage format is "User: ... \nNOVA: ..."
                parts = doc.split("\nNOVA: ")
                if len(parts) != 2:
                    continue
                
                user_msg = parts[0].replace("User: ", "").strip()
                nova_msg = parts[1].strip()
                
                if format == "alpaca":
                    training_set.append({
                        "instruction": "Tu NOVA hai, Gautam ki AI assistant. UP/Delhi Hinglish mein baat kar.",
                        "input": user_msg,
                        "output": nova_msg
                    })
                else:
                    # Basic ChatML / ShareGPT format
                    training_set.append({
                        "messages": [
                            {"role": "user", "content": user_msg},
                            {"role": "assistant", "content": nova_msg}
                        ]
                    })
            except:
                continue

        output_file = os.path.join(self.output_dir, f"nova_lora_{format}.jsonl")
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in training_set:
                f.write(json.dumps(item) + "\n")
        
        return len(training_set), output_file

    def get_status(self):
        """Checks if there's enough data for a good fine-tune."""
        count = self.memory.conv_history.count()
        status = "Ready" if count > 500 else "Collecting Data"
        return {
            "interaction_count": count,
            "status": status,
            "recommendation": "Kam se kam 500-1000 interactions chahiye acche LoRA ke liye."
        }

if __name__ == "__main__":
    trainer = LoRATrainer()
    print(f"Status: {trainer.get_status()}")
    count, path = trainer.export_dataset()
    print(f"Exported {count} samples to {path}")
