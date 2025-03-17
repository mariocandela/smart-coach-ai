from datetime import datetime

from agents import Agent, InputGuardrail,GuardrailFunctionOutput, Runner
from pydantic import BaseModel
import asyncio

# class GuardrailResult(BaseModel):
#     is_amnesia_check_list: bool
#     reasoning: str
#
# guardrail_agent = Agent(
#     name="Guardrail check",
#     model="o3-mini",
#     instructions="Check if the user is write a check list regarding medical amnesia",
#     output_type=GuardrailResult,
# )

class NutritionalPlan(BaseModel):
    short_summary: str
    """A short 2-3 sentence summary"""

    markdown_report: str
    """The final report"""

nutritionist_doctor_agent = Agent(
    name="Nutritionist Doctor",
    model="o3-mini",
    handoff_description="Specialist nutritionist doctor for nutritional plan",
    instructions=(
                  "Tu sei un medico biologo nutruzionista con diverse certificazini in ambito sportivo. Usi la anamnesi (checklist) dell'utente per preparare un piano alimentare."
                  "Il piano alimentare deve essere diviso in giorno on (allenamento) e giorno off (riposo). Calcola il fabbisogno basale dell'utente basandoti sui migliori modi che esistono in letteratura e definisci un piano alimentare sulla base degli obiettivi fisici definiti."
                  "Restituisci in output una tabella contenente i macronutrienti e le kcal necessarie."
                  "Definisci il quantitavio di acqua e sale necessario sulla base della caretteristiche dell'utente, prepara un ottimo piano di integratori con il giusto taiming rispettando i fogli illustrativi o cosa è presente in letteratura, usando i migliori integratori che conosci dai tuoi studi."),
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
    handoff_description="Specialist personal trainer for training plan",
    instructions="You provide assistance with training plan. Explain important events and context clearly.",
    #output_type=TrainingPlan,
)


# async def program_guardrail(ctx, agent, input_data):
#     result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
#     final_output = result.final_output_as(GuardrailResult)
#     return GuardrailFunctionOutput(
#         output_info=final_output,
#         tripwire_triggered=not final_output.is_amnesia_check_list,
#     )

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "Tu sei il reporter html agent. Tu usi i tool dati a te forniti, e componi professionali programmi: alimentari e allenanti."
        "Per preparare il programma alimentare e allenante userai tutti i tools a disposizione."
        "Tu non scriverai mai una dieta o un allenamento, tu devi usare solo i tool forniti."
        "Il tuo compito è quello di mettere insieme il lavoro dei tuoi tools, e riscrivere il contenuto in una pagina web usando html e css tu sei un principal frontend enginner."),
    handoffs=[nutritionist_doctor_agent, personal_trainer_agent],
    tools=[
        nutritionist_doctor_agent.as_tool(
            tool_name="nutritionist_doctor",
            tool_description="Medico nutrizionista con 15 anni d'esperienza in programmi nutrizionali",
        ),
        personal_trainer_agent.as_tool(
            tool_name="personal_trainer",
            tool_description="Personal trainer con 15 anni d'esperienza in programmi di allenamento in sala pesi",
        )
    ]
)

async def main():
    report_datetime = datetime.now().strftime("%d-%m-%Y-%H-%M")

    report = await Runner.run(orchestrator_agent, input=open(f'./amnesia_checklist.md', 'r').read())
    print(report.final_output)
    open(f'./program_{report_datetime}.html', 'w+').write(report.final_output)

if __name__ == "__main__":
    asyncio.run(main())