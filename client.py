import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic

# =============================================================================
# SETUP
# =============================================================================
API_KEY = os.environ.get("ANTHROPIC_API_KEY") 

if not API_KEY:
    print("❌ Error: ANTHROPIC_API_KEY environment variable not found")
    sys.exit(1)

server_params = StdioServerParameters(
    command=sys.executable, 
    args=["server.py"], 
    env=None
)

async def run_analysis():
    print("🚀 STARTING CONTEXT DEBT ANALYSIS SYSTEM")
    print("=========================================")

    # 1. Connection to MCP Server (Data Layer)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connection with MCP Server established.")

            # 2. Context Extraction (Using the Resources you defined)
            print("📥 Getting 'Observable Reality' (cicd://model)...")
            model_res = await session.read_resource("cicd://model")
            cicd_context = model_res.contents[0].text
            print("DEBUG: Printing first 500 characters of cicd_context")
            print(cicd_context[:500])
            print("--------------------------------------------------")

            print("📥 Getting 'Declared Intention' (intent://agents-md)...")
            try:
                intent_res = await session.read_resource("intent://agents-md")
                intent_context = intent_res.contents[0].text
                print("DEBUG: Printing first 500 characters of intent_context")
                print(intent_context[:500])
                print("--------------------------------------------------")
            except Exception:
                intent_context = "No agents.md found."
                print("⚠️ agents.md not found, analysis will be limited.")

            # 3. Building the Prompt for Claude
            print("🧠 Consulting Claude Sonnet 4.5")
            
            prompt = f"""
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

            # 4. Call to Anthropic API
            client = Anthropic(api_key=API_KEY)
            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1000,
                temperature=0,
                system="You are a static context debt analyzer. You must be precise and concise without being overly verbose and WITHOUT ADDING INFORMATION that is not provided by the CONTEXT.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 5. Display Result
            print("\n📊 CONTEXT DEBT REPORT GENERATED:")
            print("==================================")
            print(message.content[0].text)
            print("==================================")

if __name__ == "__main__":
    asyncio.run(run_analysis())