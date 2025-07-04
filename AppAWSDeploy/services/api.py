import json
from nitric.resources import api
from nitric.application import Nitric
from nitric.context import HttpContext
import pandas as pd
from auth import verify_token  # Make sure this path is correct

# Load population data
df = pd.read_csv("services/Data/2021_population.csv")

# Create API instance
main = api("population-api")

@main.get("/population")
async def get_population(ctx: HttpContext):
    # Step 1: Verify JWT token first
    try:
        verify_token(ctx)
    except Exception as auth_error:
        ctx.res.status = 401
        ctx.res.body = json.dumps({"error": str(auth_error)})
        ctx.res.headers["Content-Type"] = "application/json"
        return

    try:
        country = ctx.req.query.get("country", [""])[0].strip()
        year = ctx.req.query.get("year", [""])[0].strip()

        column_map = {
            "2020": "2020_population",
            "2021": "2021_last_updated"
        }

        if not country or not year:
            ctx.res.status = 400
            ctx.res.body = json.dumps({"error": "Missing 'country' or 'year' parameter"})
            ctx.res.headers["Content-Type"] = "application/json"
            return

        column_name = column_map.get(year)
        if not column_name:
            ctx.res.status = 404
            ctx.res.body = json.dumps({"error": f"No data available for year {year}"})
            ctx.res.headers["Content-Type"] = "application/json"
            return

        result_row = df[df["country"].str.lower() == country.lower()]
        if result_row.empty:
            ctx.res.status = 404
            ctx.res.body = json.dumps({"error": f"No data found for country '{country}'"})
            ctx.res.headers["Content-Type"] = "application/json"
            return

        population_raw = result_row.iloc[0][column_name]
        try:
            population_clean = int(str(population_raw).replace(",", "").strip())
        except ValueError:
            ctx.res.status = 500
            ctx.res.body = json.dumps({"error": "Invalid population data format"})
            ctx.res.headers["Content-Type"] = "application/json"
            return

        response = {
            "country": country,
            "year": year,
            "population": population_clean
        }

        print("Sending response:", response)
        ctx.res.body = json.dumps(response)
        ctx.res.headers["Content-Type"] = "application/json"
        return

    except Exception as e:
        ctx.res.status = 500
        ctx.res.body = json.dumps({"error": str(e)})
        ctx.res.headers["Content-Type"] = "application/json"

# Start the app
Nitric.run()
