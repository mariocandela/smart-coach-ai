from datetime import datetime

from agents import Agent, InputGuardrail,GuardrailFunctionOutput, Runner
from pydantic import BaseModel
import asyncio

class GuardrailResult(BaseModel):
    is_amnesia_check_list: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    model="o3-mini",
    instructions="Check if the user is write a check list regarding medical amnesia",
    output_type=GuardrailResult,
)

class NutritionalPlan(BaseModel):
    short_summary: str
    """A short 2-3 sentence summary"""

    markdown_report: str
    """The final report"""

nutritionist_doctor_agent = Agent(
    name="Nutritionist Doctor",
    model="o3-mini",
    handoff_description="Specialist nutritionist doctor agent for nutritional plan",
    instructions="You provide help with nutritional plan. Explain your reasoning at each step and include examples",
    #output_type=NutritionalPlan,
)

class TrainingPlan(BaseModel):
    short_summary: str
    """A short 2-3 sentence summary."""

    markdown_report: str
    """The final report"""

personal_trainer_agent = Agent(
    name="Personal trainer",
    model="o3-mini",
    handoff_description="Specialist personal trainer agent for training plan",
    instructions="You provide assistance with training plan. Explain important events and context clearly.",
    #output_type=TrainingPlan,
)


async def program_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(GuardrailResult)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_amnesia_check_list,
    )

reporter_export = Agent(
    name="Studio medico",
    instructions="Sei il coordinatore di uno studio medico con 15 anni di esperienza e il tuo compito è gestire il lavoro del nutrizionista e del personal trainer. Analizza i dati forniti nella check-list anamnestica dell'utente, integra le informazioni di entrambi i professionisti e crea un programma personalizzato ottimale. Presenta il piano in modo chiaro e strutturato, utilizzando tabelle e schemi esplicativi per facilitare la comprensione.",
    handoffs=[nutritionist_doctor_agent, personal_trainer_agent],
    tools=[
        nutritionist_doctor_agent.as_tool(
            tool_name="nutritionist_doctor",
            tool_description="Medico nutrizionista con 15 anni d'esperienza in piani nutrizionali",
        ),
        personal_trainer_agent.as_tool(
            tool_name="personal_trainer",
            tool_description="Personal trainer con 15 anni d'esperienza in piani di allenamento in sala pesi",
        )
    ]
)

async def main():
    report_datetime = datetime.now().strftime("%d-%m-%Y-%H-%M")

    report = await Runner.run(reporter_export, input=open(f'./amnesia_checklist.md', 'r').read())
    print(report.final_output)
    open(f'./program_{report_datetime}.md', 'w+').write(report.final_output)

if __name__ == "__main__":
    asyncio.run(main())