from langchain.agents import tool
import googlemaps
import os

# ==============================
#  THERAPIST TOOL (LIGHTWEIGHT)
# ==============================
@tool
def ask_mental_health_specialist(query: str) -> str:
    """
    Use this for emotional support, mental health questions,
    or empathetic conversation.
    """
    # Let main LLM handle response
    return f"User is seeking emotional support: {query}"


# ==============================
#  GOOGLE MAPS TOOL
# ==============================
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)


@tool
def find_nearby_therapists_by_location(location: str) -> str:
    """
    Finds real therapists near the specified location.
    """
    try:
        geocode_result = gmaps.geocode(location)

        if not geocode_result:
            return f"Couldn't find location: {location}"

        lat_lng = geocode_result[0]['geometry']['location']
        lat, lng = lat_lng['lat'], lat_lng['lng']

        places_result = gmaps.places_nearby(
            location=(lat, lng),
            radius=5000,
            keyword="Psychotherapist"
        )

        results = places_result.get('results', [])[:5]

        if not results:
            return f"No therapists found near {location}"

        output = [f"Therapists near {location}:"]

        for place in results:
            name = place.get("name", "Unknown")
            address = place.get("vicinity", "Address not available")

            details = gmaps.place(
                place_id=place["place_id"],
                fields=["formatted_phone_number"]
            )

            phone = details.get("result", {}).get(
                "formatted_phone_number",
                "Phone not available"
            )

            output.append(f"- {name} | {address} | {phone}")

        return "\n".join(output)

    except Exception as e:
        print("Maps error:", e)
        return " Unable to fetch therapists right now. Please try again later."