import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import markdown2

# ✅ Set OpenAI API Key (you can comment this out if using env var)
os.environ["OPENAI_API_KEY"] = " Secret key"

# ✅ Initialize the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# === AGENTS ===
location_expert = Agent(
    role="Travel Trip Expert",
    goal="Gathers helpful information about the city during travel.",
    backstory="A seasoned traveler who has explored various destinations and knows the ins and outs of travel logistics.",
    tools=[], verbose=True, max_iter=5, llm=llm,
)

guide_expert = Agent(
    role="City Local Guide Expert",
    goal="Provides information on things to do in the city based on the user's interests.",
    backstory="A local expert with a passion for sharing the best experiences and hidden gems of their city.",
    tools=[], verbose=True, max_iter=5, llm=llm,
)

planner_expert = Agent(
    role="Travel Planning Expert",
    goal="Compiles all gathered information to provide a comprehensive travel plan.",
    backstory="An organizational wizard who can turn a list of possibilities into a seamless itinerary.",
    tools=[], verbose=True, max_iter=5, llm=llm,
)

# === TASKS ===
def location_task(agent, from_city, destination_city, date_from, date_to):
    return Task(
        description=f"""
        Gather essential travel information for {destination_city}, including:
        - Accommodation options
        - Cost of living
        - Weather
        - Transportation
        - Local events
        Dates: {date_from} to {date_to}
        """,
        expected_output="Markdown report with travel logistics and useful tips.",
        agent=agent,
        output_file="city_report.md"
    )

def guide_task(agent, destination_city, interests, date_from, date_to):
    return Task(
        description=f"""
        Create a local guide for {destination_city} tailored to: {interests}.
        Include best spots to visit, eat, relax, and explore during {date_from} to {date_to}.
        """,
        expected_output="Markdown with interactive places, events, food, attractions.",
        agent=agent,
        output_file="guide_report.md"
    )

def planner_task(context, agent, destination_city, interests, date_from, date_to):
    return Task(
        description=f"""
        Create a complete travel plan for {destination_city} based on previous agent outputs.
        Include:
        - Introduction (4 short paras)
        - Budget breakdown
        - Daily plan with timing
        - Transport and booking tips
        Interests: {interests}, Dates: {date_from} to {date_to}
        """,
        expected_output="Full travel itinerary in Markdown format.",
        context=context,
        agent=agent,
        output_file="travel_plan.md"
    )

# === CREW RUNNER ===
def run_crew(from_city, destination_city, date_from, date_to, interests):
    loc_task = location_task(location_expert, from_city, destination_city, date_from, date_to)
    guid_task = guide_task(guide_expert, destination_city, interests, date_from, date_to)
    plan_task = planner_task([loc_task, guid_task], planner_expert, destination_city, interests, date_from, date_to)

    crew = Crew(
        agents=[location_expert, guide_expert, planner_expert],
        tasks=[loc_task, guid_task, plan_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    # Save final output to markdown file
    output_text = getattr(result, "final_output", str(result))
    md_path = f"travel_plan_{destination_city}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(output_text)

    return result, md_path  # return both output and path

# === PDF GENERATOR (reportlab-based) ===
def convert_md_to_pdf(md_path, pdf_path="travel_plan.pdf"):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html = markdown2.markdown(md_content)

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    for line in html.splitlines():
        if line.strip():  # Skip empty lines
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    return pdf_path