import os
from datetime import datetime

# -------------------------------
# Configuration
# -------------------------------
CORE_ROOT = os.path.join(os.path.dirname(__file__))
LOG_FILE = os.path.join(CORE_ROOT, "../../data/logs/self_repair.log")

# Full core structure (folders and empty module files)
CORE_STRUCTURE = {
    "adapters": ["base_adapter.py", "mock_adapters.py", "real_adapters.py"],
    "consciousness": ["__init__.py"],
    "consciousness/attention": ["monitor.py", "focus_control.py", "resource_allocation.py"],
    "consciousness/metacognition": ["monitoring.py", "evaluation.py", "reflection.py"],
    "consciousness/self_model": ["introspection.py", "goal_formation.py", "belief_system.py"],
    "reasoning": ["__init__.py"],
    "reasoning/causal": ["discovery.py", "inference.py", "intervention.py"],
    "reasoning/abstract": ["pattern_recognition.py", "generalization.py", "application.py"],
    "reasoning/logical": ["inference_engine.py", "validation.py", "deduction.py"],
    "reasoning/probabilistic": ["inference.py", "sampling.py", "optimization.py"],
    "reasoning/common_sense": ["knowledge.py", "inference.py", "application.py"],
    "understanding": ["__init__.py"],
    "understanding/language": ["parsing.py", "semantics.py", "pragmatics.py"],
    "understanding/concepts": ["representation.py", "organization.py", "learning.py"],
    "understanding/context": ["inference.py", "maintenance.py", "update.py"],
    "understanding/multimodal": ["fusion.py", "grounding.py", "integration.py"],
    "learning": ["__init__.py"],
    "learning/continual": ["task_learning.py", "retention.py", "transfer.py"],
    "learning/few_shot": ["adaptation.py", "generalization.py", "optimization.py"],
    "learning/meta": ["strategy_learning.py", "optimizer.py", "evaluation.py"],
    "learning/transfer": ["source_selection.py", "adaptation.py", "validation.py"],
    "memory": ["__init__.py"],
    "memory/episodic": ["storage.py", "retrieval.py", "consolidation.py"],
    "memory/semantic": ["knowledge_base.py", "reasoning.py", "update.py"],
    "memory/procedural": ["skill_learning.py", "execution.py", "optimization.py"],
    "memory/working": ["buffer.py", "attention.py", "manipulation.py"],
    "creativity": ["__init__.py"],
    "creativity/generative": ["ideation.py", "refinement.py", "evaluation.py"],
    "creativity/analogical": ["mapping.py", "transfer.py", "adaptation.py"],
    "creativity/conceptual": ["blending.py", "emergence.py", "combination.py"],
    "emotion": ["__init__.py"],
    "emotion/recognition": ["detection.py", "classification.py", "modeling.py"],
    "emotion/generation": ["appraisal.py", "valence_arousal.py", "dynamics.py"],
    "emotion/integration": ["memory_binding.py", "decision_influence.py", "expression.py"],
    "social": ["__init__.py"],
    "social/theory_of_mind": ["modeling.py", "prediction.py", "reasoning.py"],
    "social/communication": ["language_generation.py", "language_understanding.py", "dialogue.py"],
    "social/cooperation": ["collaboration.py", "coordination.py", "negotiation.py"],
    "planning": ["__init__.py"],
    "planning/goals": ["formation.py", "prioritization.py", "decomposition.py"],
    "planning/actions": ["generation.py", "constraints.py", "execution.py"],
    "planning/reasoning": ["means_ends.py", "temporal.py", "optimization.py"],
    "evolution": ["__init__.py"],
    "evolution/self_modification": ["analysis.py", "modification.py", "testing.py"],
    "evolution/architecture_search": ["search_space.py", "evaluation.py", "optimization.py"],
    "evolution/capability_expansion": ["discovery.py", "integration.py", "validation.py"],
}

# -------------------------------
# Logging
# -------------------------------
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {message}\n")
    print(f"[SELF-REPAIR] {message}")

# -------------------------------
# Build / Repair Function
# -------------------------------
def build_core():
    folders_created = 0
    files_created = 0

    for rel_path, files in CORE_STRUCTURE.items():
        folder_path = os.path.join(CORE_ROOT, rel_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            folders_created += 1
            log(f"Created folder: {folder_path}")
        # Ensure __init__.py exists in every folder
        init_file = os.path.join(folder_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8") as f:
                f.write("# Auto-generated __init__.py\n")
            files_created += 1
            log(f"Created __init__.py in {folder_path}")

        # Create module files
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"# Auto-generated {file_name}\n")
                files_created += 1
                log(f"Created module: {file_path}")

    log(f"CORE BUILD COMPLETE: {folders_created} folders, {files_created} files created or repaired.")

# -------------------------------
# Run Repair / Build
# -------------------------------
if __name__ == "__main__":
    log("Starting self-repair / build sequence...")
    build_core()
    log("Self-repair / build finished successfully.")
