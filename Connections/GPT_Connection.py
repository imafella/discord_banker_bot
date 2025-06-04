from openai import OpenAI
import os, asyncio

class GPTConnection:
    def __init__(self, name:str, instructions:str, tools:list=None, model:str="gpt-4o"):
        self.client = OpenAI(api_key=os.getenv("open_ai_api_key"))
        self.assistant_id = os.getenv("tyler_bot_id", None)
        self.assistant = None
        self.create_assistant(assistant_id=self.assistant_id, name=name, instructions=instructions, tools=tools, model=model)
        self.name = name
        self.instructions = instructions
        self.tools = tools if tools is not None else []
        self.model = model
        self.thread = self.create_thread()


    def create_assistant(self, name:str, instructions:str=None, tools:list=None, model:str="gpt-4o", assistant_id:str=None):
        if assistant_id:
            # If an assistant ID is provided, retrieve the existing assistant
            assistant = self.client.beta.assistants.retrieve(assistant_id)
            if instructions and assistant.instructions != instructions:
                self.assistant = assistant
                assistant = self.update_assistant_instructions(instructions)
        else:
            assistant = self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=tools,
            model=model,
        )
        self.assistant = assistant

    def update_assistant_instructions(self, instructions:str):
        if self.assistant:
            self.assistant.instructions = instructions
            updated_assistant = self.client.beta.assistants.update(
                assistant_id=self.assistant_id,
                instructions=instructions
            )
            self.assistant = updated_assistant
    
    def create_thread(self):
        thread = self.client.beta.threads.create()
        return thread
    
    async def add_message(self, role:str, content:str):
        await asyncio.to_thread(
            self.client.beta.threads.messages.create,
            thread_id=self.thread.id,
            role=role,
            content=content
        )
        await asyncio.sleep(0.5)  # Allow time for the message to be processed
    async def get_msg_response(self):
        run = await asyncio.to_thread(
            self.client.beta.threads.runs.create_and_poll,
            thread_id=self.thread.id,
            assistant_id=self.assistant_id
        )

        while True:
            await asyncio.sleep(1)
            run_status = await asyncio.to_thread(
                self.client.beta.threads.runs.retrieve,
                thread_id=self.thread.id, 
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "cancelled", "expired"]:
                raise Exception(f"Run failed with status: {run_status.status}")


        
            # Retrieve the messages from the thread
        messages = await asyncio.to_thread(
            self.client.beta.threads.messages.list,
            thread_id=self.thread.id
        )

        # Fallback: return latest assistant message
        for msg in messages.data:
            if msg.role == "assistant":
                return msg.content[0].text.value

        return "No response from assistant."
    