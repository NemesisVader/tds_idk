from fastapi import FastAPI, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Union
import json
from datetime import datetime
import uvicorn
import os

# Replace this with your IIT‑M email
YOUR_EMAIL = "23f2004203@ds.study.iitm.ac.in"

# Load the dataset once at startup
DATA_PATH = os.path.join(os.path.dirname(__file__), "q-fastapi-llm-query.json")
with open(DATA_PATH, "r") as f:
    data = json.load(f)

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/query")
def query(q: str = Query(..., description="Natural‑language question"), response: Response = None):
    # Always include your email
    response.headers["X-Email"] = YOUR_EMAIL

    q_lower = q.lower()
    answer: Union[str, int] = "Not Found"

    # 1) Total sales of <Product> in <City>
    if "total sales of" in q_lower and "in" in q_lower:
        parts = q_lower.split("total sales of")[1].split("in")
        product = parts[0].strip().title()
        city = parts[1].replace("?", "").strip().title()
        total = sum(
            entry["sales"]
            for entry in data
            if entry["product"] == product and entry["city"] == city
        )
        answer = total

    # 2) How many sales reps are there in <Region>
    elif "how many sales reps" in q_lower and "in" in q_lower:
        region = q_lower.split("in")[1].replace("?", "").strip().title()
        reps = {entry["rep"] for entry in data if entry["region"] == region}
        answer = len(reps)

    # 3) Average sales for <Product> in <Region>
    elif "average sales for" in q_lower and "in" in q_lower:
        parts = q_lower.split("average sales for")[1].split("in")
        product = parts[0].strip().title()
        region = parts[1].replace("?", "").strip().title()
        filtered_sales = [
            entry["sales"]
            for entry in data
            if entry["product"] == product and entry["region"] == region
        ]
        answer = round(sum(filtered_sales) / len(filtered_sales)) if filtered_sales else 0

    # 4) On what date did <Rep> make the highest sale in <City>?
    elif "make the highest sale in" in q_lower and q_lower.startswith("on what date did"):
        # Extract rep name (between "did " and " make")
        rep_raw = q_lower.split("did")[1].split("make")[0].strip()
        # Capitalize each word (handles multi‑word names & titles)
        rep = " ".join(w.title() for w in rep_raw.split())
        city = q_lower.split("in")[1].replace("?", "").strip().title()

        # Find all matching entries
        rep_entries = [e for e in data if e["rep"] == rep and e["city"] == city]
        if rep_entries:
            best = max(rep_entries, key=lambda e: e["sales"])
            answer = best["date"]
        else:
            answer = "N/A"

    return {"answer": answer}


if __name__ == "__main__":
    # adjust module name as needed if you rename this file
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
