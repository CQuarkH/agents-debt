import asyncio
import os
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic


from steering import build_context_debt_prompt

# =============================================================================
# SETUP
# =============================================================================
API_KEY = os.environ.get("ANTHROPIC_API_KEY") 

if not API_KEY:
    print("❌ Error: ANTHROPIC_API_KEY environment variable not found")
    sys.exit(1)
    
    
CURRENT_DIR = Path(__file__).parent
SERVER_SCRIPT = CURRENT_DIR.parent / "mcp_server" / "server.py"

server_params = StdioServerParameters(
    command=sys.executable, 
    args=[str(SERVER_SCRIPT)], 
    env=None
)

async def main():
    print("🚀 STARTING CONTEXT DEBT ANALYSIS SYSTEM (HOST)")
    print("==============================================")

    # 1. Connection to MCP Server (Data Layer)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connection with MCP Server established.")

            # 2. Context Extraction (Consumption of Resources)
            print("📥 Fetching Resources from Server...")
            
            # Fetch Reality
            model_res = await session.read_resource("cicd://model")
            cicd_context = model_res.contents[0].text
            print("DEBUG: Printing first 500 characters of cicd_context")
            print(cicd_context[:500])
            print("--------------------------------------------------")
            
            # Fetch Intent
            try:
                intent_res = await session.read_resource("intent://agents-md")
                intent_context = intent_res.contents[0].text
                print("DEBUG: Printing first 500 characters of intent_context")
                print(intent_context[:500])
                print("--------------------------------------------------")
                
            except Exception:
                intent_context = "No agents.md found."
                print("⚠️ Warning: agents.md not found.")
                
            # 3. Steering Layer (MOCK)
            print("🧠 Applying Steering (Building Prompt)...")
            final_prompt = build_context_debt_prompt(cicd_context, intent_context)

            # 4. Inference Layer (Call to Anthropic)
            print("🤖 Calling Claude Sonnet 4.5...")
            client = Anthropic(api_key=API_KEY)
            
            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1000,
                temperature=0,
                system="You are a static context debt analyzer. You must be precise and concise without being overly verbose and WITHOUT ADDING INFORMATION that is not provided by the CONTEXT.",
                messages=[
                    {"role": "user", "content": final_prompt}
                ]
            )

            # 5. Presentation Layer
            print("\n📊 CONTEXT DEBT REPORT GENERATED:")
            print("==================================")
            print(message.content[0].text)
            print("==================================")

if __name__ == "__main__":
    asyncio.run(main())