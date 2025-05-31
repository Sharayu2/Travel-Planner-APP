import streamlit as st
from datetime import date
from backend_module import run_crew, convert_md_to_pdf

# === UI Header ===
st.set_page_config(page_title="AI Trip Planner", layout="centered")
st.title("🌍 AI-Powered Travel Planner")

st.markdown("""
Plan your dream vacation using AI-powered agents!  
Get personalized recommendations, local tips, daily itinerary, and a downloadable travel plan.  
""")

# === User Inputs ===
with st.form("trip_form"):
    from_city = st.text_input("🏠 Starting City", "India")
    destination_city = st.text_input("🗺️ Destination City", "Rome")
    date_from = st.date_input("📅 Departure Date", value=date.today())
    date_to = st.date_input("📅 Return Date")
    interests = st.text_area("🎯 Your Interests", "Sightseeing, food, and local culture")

    submit = st.form_submit_button("🚀 Generate My Travel Plan")

# === Generate Output ===
if submit:
    if not all([from_city, destination_city, date_from, date_to, interests]):
        st.error("Please fill in all fields.")
    else:
        with st.spinner("🛫 Planning your trip..."):
            result, md_path = run_crew(from_city, destination_city, date_from, date_to, interests)
            st.success("✅ Your travel plan is ready!")

            st.subheader("🧳 Itinerary Summary")
            output_text = getattr(result, "final_output", str(result))
            st.markdown(output_text)
            

            # ✅ Download as Text
            st.download_button(
                label="📥 Download as Text",
                data=output_text,
                file_name=f"Travel_Plan_{destination_city}.txt",
                mime="text/plain"
            )

            # ✅ Generate and Download PDF
            try:
                pdf_path = convert_md_to_pdf(md_path, pdf_path=f"Travel_Plan_{destination_city}.pdf")
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📄 Download Full PDF",
                        data=f,
                        file_name=f"Travel_Plan_{destination_city}.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.warning(f"⚠️ PDF creation failed: {e}")
