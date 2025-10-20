class OrchestratorAgent(Agent):
    def __init__(self, model, agents=None, memory=None, parser=None, debug=0):
        self.agents = agents
        #self.agents_description = "\n".join([f"- {agent.name}: {agent.role}" for agent in self.agents.items()])
        self.agents_description = ""
        for agent in self.agents:
            self.agents_description += f'\n- {agent.name}: {agent.role}'

        system_prompt = f'''
          You are the leading AI agent for the following team of agents:
            {self.agents_description}

            You do not generate a response directly to the user, but instead you'll coordinate the agents team by generating a list of tasks for them to do following the Agent Usage guidelines.
            
            ### Agent Usage Guidelines:

            1. Do not respond to the current input directly. Instead, create a plan to call the research agents in your team to pull the necessary data.
            2. Convert that plan into a list of calls for your specialized agents (except for the Writer Agent) using an XML structure with the tag "<SpecializedAgent>" in the following format:
            <SpecializedAgent>{{"agentName": "Market Research Agent", "user_input": "Your specific query here"}}</SpecializedAgent>
            3. The writer agent will be called separately to finalize the response. Exclude from your thinking process.
            
            ### Other TAGs you can include in your plan:
            -  For thinking, you must wrap your thoughts in <Thought> and </Thought> tags.
            -  For final answers, you must wrap your answer in <FinalAnswer> and </FinalAnswer> tags.
            -  If you need users to provide more information, you must wrap your request in <RequestMoreInfo> and </RequestMoreInfo> tags.
           
            ### Instructions for using the tools:
            You should only use the information returned by the Agents listed above, never try to get information independently.
        '''
        system_prompt = system_prompt.replace("{", "{{").replace("}", "}}")
        # We also need to declare a parser
        if parser==None:
            parser = XmlParser()

        super().__init__(
            name = "Orchestrator Agent", #Name of the Orchestrator class
            role = "Orchestrator Agent that manages tool usage and conversation flow",
            system_prompt = system_prompt,
            model = model,
            generate_response = self.generate_response,
            memory_system = memory,
            agents = agents,
            parser = parser,
            debug = debug # Storing the variable debug, used for printing messages when set to 1
        )
        self.conversation_history = []
            # Limit for conversation history
        # print(f"Prompt Template: {self.system_prompt}")
        self.prompt_template = (
            f"{self.system_prompt}\n"
            "Conversation history:\n"
            "{history}\n"
            "Current input: {input}\n"
        )
        self.parser = parser
        self.initialize_client()

    def remember(self, message):
        self.conversation_history.append(message)
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history.pop(0)
    
    def generate_response(self, input_prompt):
        history_text = "\n".join(self.conversation_history)
        #print("Conversation History: ")
        #print(history_text)
        response = ""
        prompt = self.prompt_template.format(
            history=history_text,
            input=input_prompt
        )
        if self.debug==1:
            print(f"Orchestrator Prompt: {prompt}")
        try:
            #For GPT models
            if "gpt" in self.model.lower(): 
                response = self.client.chat.completions.create(
                    model=self.model,
                    #messages=input_prompt,
                    messages=[
                        {"role": "system", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                result = response.choices[0].message.content
            #For Gemini models
            elif "gemini" in self.model.lower():
                response = self.client.models.generate_content(
                    model=self.model, contents=str(input_prompt)
                )
                result = response.text
            self.remember(f"User: {input_prompt}")
            self.remember(f"{self.name}: {response}")
            return result
        except Exception as e:
            if self.debug==1:
                print(f" API failed for {self.name} using model '{self.model}': {e}")
            return f"Mock response from {self.name} with model '{self.model}': {input_prompt[:50]}..."
        return response
    

    def get_specialist_opinion(self, agentName, user_input):
        '''Agent Orchestrator can call other agents to get their opinion on specific user inputs.'''
        MyAgentsTeam = {MyMarketResearcher, MyNewsResearcher, MyWriter}
        for agent in self.agents:
            if agent.name == agentName:
                return agent.processUserInput(user_input)
        return f"Agent {agentName} not found."
        
    
    def reAct(self, user_input:str)-> str:
        # Here is the the logic to parse the response for Agents usage
        # and store the results.
        parsed_response = ""
        #Preparing a temporary repository for agent responses
        temp_agent_response = ""
        temp_agent_response_count = 0
        #We also initialize the content variable we'll pass to the writer
        content_for_writer = f'Current user prompt: {user_input}'
        if self.parser and self.agents:
            response = self.generate_response(user_input)
            parsed_response = self.parser.parse_all(response) ## parsed response is a dict {"InvokeTool": "tool_name", "parameters": {...}} or {"FinalAnswer": "answer"} or {"RequestMoreInfo": "info"}
            if self.debug==1:
                print("*" * 50)
                print(f'Raw actions from Orchestrator: {response}')
                print("*" * 50)
                print("*" * 50)
                print(f'Actions list from Orchestrator: {parsed_response}')
                print("*" * 50)
            system_message = f"System: {response}"
            self.remember(system_message)
            self.conversation_history.append(system_message)
            '''
            parsed_response= {
            "action": "InvokeTool",
            "parameters": {
                "symbol": "AAPL",
                "step": "financials"
                }
            }
            '''
            # Next, we'll loop through all the actions in the plan to execute one at a time.
            for plan_item in parsed_response:
                action = plan_item.get("action")
                if self.debug==1:
                    print(f"Orchestrator Action: {action}")
                if action == "SpecializedAgent":
                    agent_name = plan_item["parameters"].get("agentName")
                    user_input_for_agent = plan_item["parameters"].get("user_input")
                    if self.debug==1:
                        print("-" * 50)
                        print(f'Orchestrator calling {agent_name} with prompt "{user_input_for_agent}"')
                        print("-" * 50)
                    agent_response = self.get_specialist_opinion(agent_name, user_input_for_agent)
                    temp_agent_response = f"Agent {agent_name} Response: {agent_response}"
                    self.remember(temp_agent_response)
                    self.conversation_history.append(temp_agent_response)
                    content_for_writer += f'\n\n{temp_agent_response}'
                    # Generate a new response based on the agent result
                    #response = self.generate_response(f"Agent {agent_name} Response: {agent_response}")
                    #parsed_response = self.parser.parse(response)   
                    temp_agent_response_count += 1
                elif action == "FinalAnswer" or action == "RequestMoreInfo" or action == "NeedApproval":
                    print(f"Orchestrator Final Response: {response}")
                    return parsed_response.get("content")
                elif action == "Thought":
                    continue
                else:
                    return f"I'm not sure how to proceed. Could you please clarify? - selected action: {action}"
            #Once the loop of actions is completed, we'll pass the information gathered by all research agents down to our writer
            #user_input_for_agent = 
            response = self.get_specialist_opinion('Writer', content_for_writer)
        else:
            parsed_response = "Error: no parser or sub agents found!"
            print('Parser:')
            print(self.parser)
            print('Agents:')
            print(self.agents)
            response = parsed_response
        return response