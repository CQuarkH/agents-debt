import asyncio
import sys
import os
import json
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from steering.context_debt import ContextDebtPolicy

# SETUP

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
CURRENT_DIR = Path(__file__).parent
SERVER_SCRIPT = CURRENT_DIR.parent / "mcp_server" / "server.py"

server_params = StdioServerParameters(
    command=sys.executable,
    args=[str(SERVER_SCRIPT)],
    env=None
)

async def main():
    print("🚀 HOST: Initializing Context Debt Analysis...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. INGESTION
            print("📥 HOST: Fetching Domain Model & Intent...")
            
            # Get the Domain Model (The Structured Reality)
            model_res = await session.read_resource("cicd://model")
            # Parse the JSON to Python Dictionary so constraints.py can work with it
            domain_model_dict = json.loads(model_res.contents[0].text)
            
            # Get the Intent (The Text)
            try:
                intent_res = await session.read_resource("intent://agents-md")
                intent_text = intent_res.contents[0].text
            except Exception:
                intent_text = "No documentation found."

            # 2. STEERING (Apply the Policy)
            print("🧠 HOST: Applying Steering Policy (Defining Structural Boundaries)...")
            
            # Instantiate the specific policy
            policy = ContextDebtPolicy()
            
            # Generate the final Prompt based on constraints
            final_prompt = policy.assemble_prompt(
                domain_model=domain_model_dict, 
                intent_context=intent_text
            )
            
            # (Optional) Debug: View generated constraints
            # print(policy.compute_constraints(domain_model_dict))

            # 3. INFERENCE (LLM Execution)
            print("🤖 HOST: Sending constrained task to LLM...")
            client = Anthropic(api_key=API_KEY)
            
            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1500,
                temperature=0, # Temperature 0 is vital for strict compliance tasks
                messages=[{"role": "user", "content": final_prompt}]
            )

            print("\n" + "="*50)
            print("📊 CONTEXT DEBT SMELLS REPORT")
            print("="*50)
            print(message.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())