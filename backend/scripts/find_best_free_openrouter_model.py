import asyncio
import json
import urllib.request
import time
from openai import AsyncOpenAI
import os

# Put your OpenRouter API key here or set via env var
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

async def fetch_free_models():
    """Fetches all models from OpenRouter and filters for free ones."""
    url = "https://openrouter.ai/api/v1/models"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
    free_models = []
    for model in data.get("data", []):
        pricing = model.get("pricing", {})
        prompt_price = float(pricing.get("prompt", -1))
        completion_price = float(pricing.get("completion", -1))
        
        # Consider free if both are 0, or if the ID ends with :free
        if (prompt_price == 0 and completion_price == 0) or ":free" in model["id"]:
            free_models.append(model)
            
    return free_models

async def test_model(client: AsyncOpenAI, model_id: str):
    """Tests a specific model for response time and JSON capability."""
    prompt = "Reply with a simple JSON object: {\"status\": \"ok\", \"model\": \"[your model name]\"}"
    start_time = time.time()
    try:
        response = await client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=10.0 # Strict timeout to filter out slow models
        )
        latency = time.time() - start_time
        content = response.choices[0].message.content
        return {"model": model_id, "latency": latency, "success": True, "error": None, "response": content}
    except Exception as e:
        latency = time.time() - start_time
        return {"model": model_id, "latency": latency, "success": False, "error": str(e), "response": None}

async def main():
    if not OPENROUTER_API_KEY:
        print("ERROR: Please set OPENROUTER_API_KEY in the environment or directly in the script.")
        return

    print("Fetching models from OpenRouter...")
    free_models = await fetch_free_models()
    print(f"Found {len(free_models)} free models. Testing them now...")
    
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    
    results = []
    for m in free_models:
        model_id = m["id"]
        print(f"Testing {model_id}...")
        res = await test_model(client, model_id)
        results.append(res)
        # small sleep to avoid rate limits
        await asyncio.sleep(1)
        
    # Filter successful ones and sort by latency
    successful = [r for r in results if r["success"]]
    successful.sort(key=lambda x: x["latency"])
    
    print("\n--- RESULTS ---")
    if not successful:
        print("No models succeeded within the 10-second timeout.")
    else:
        print("Top 5 fastest free models that support JSON output:")
        for r in successful[:5]:
            print(f"Model: {r['model']} | Latency: {r['latency']:.2f}s | Response: {r['response'][:50]}...")
            
    print("\nErrors (for reference):")
    for r in results:
        if not r["success"]:
            print(f"- {r['model']}: {r['error']}")

if __name__ == "__main__":
    asyncio.run(main())
