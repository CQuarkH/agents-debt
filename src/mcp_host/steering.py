###
# MOCK STEERING MODULE. THIS WILL BE REPLACED AND IMPLEMENTED FULLY LATER.
# ACTUALLY, THIS IS JUST TO ISOLATE THE PROMPT ENGINEERING FROM THE MAIN LOGIC.
###

def build_context_debt_prompt(cicd_context: str, intent_context: str) -> str:
    """
    Builds the prompt for context debt analysis.
    Separates 'Prompt Engineering' from execution logic.
    """
    return f"""
    Act as an Expert in DevOps and Technical Debt. Your task is to analyze "Context Debt".
            
            YOU have two sources of information:
            1. THE REALITY (What actually runs in GitHub Actions):
            {cicd_context}

            2. THE INTENTION (What the team or an AI agent says it does in the documentation):
            {intent_context}

            TASK:
            Compare Reality vs Intention.
            - Are there workflows that exist in the code but aren't mentioned in the documentation?
            - Does the documentation mention old versions or tools that are no longer used in the YAML?
            - List the discrepancies found.
    """