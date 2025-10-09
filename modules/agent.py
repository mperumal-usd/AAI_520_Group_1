class Agent:
    def __init__(self, name, model, memory, parser=None):
        self.name = name
        self.model = model
        self.memory = memory
        self.conversation_history = []
        self.tools = []
        self.max_history_length = 10 
        self.parser = parser
        # Limit for conversation history
        '''
        You are a helpful Finance assistant that explains things in a few words.
          You have the following tools:
            {tools}
        
            ### Instructions for using the tools:
            You should only use the tools listed above.
            When you use a tool, you must call the API exactly as shown above.
            You must always include the symbol in the API call.
            You must always include the step in the API call.
            You must always use double quotes for the JSON keys and string values in the API call.
            You must never use single quotes in the API call.
            You must never call any API that is not listed above.
            You must never make up any API calls.
            You must never repeat any steps.
            
            Here is an example of how to use the tools:
            User : What is the company overview for "AAPL".
            Assistant : To gather the company overview, I will use the "Company Overview" tool.
            Assistant : <InvokeTool>{"symbol": "AAPL", "step": "info"}</InvokeTool>
            Tool : <ToolResult>{"name": "Company Overview", "result": {"companyName": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"}}</ToolResult>
            Assistant : <Thought>Based on the company overview, Apple Inc. is a leading technology company in the consumer electronics industry.</Thought>
            
            ### TAGs for tool usage:
            - To use a tool, you must wrap the API call in <InvokeTool> and </InvokeTool> tags.
            -  For thinking, you must wrap your thoughts in <Thought> and </Thought> tags.
            -  For final answers, you must wrap your answer in <FinalAnswer> and </FinalAnswer> tags.
            -  If you need users to provide more information, you must wrap your request in <RequestMoreInfo> and </RequestMoreInfo> tags.
            -  If you are going to use a tool, you must always think first. Get the concern of the user query with <NeedApproval>, decide which tool to use, and then use the tool.
           
            ### Thinking Process: 
              Based on the user query, decide which tools to use and in what order.
              After using a tool, analyze the result and decide the next step.
              Continue this process until you have enough information to answer the user's query.
              Finally, provide a comprehensive answer to the user's query.
        '''
        self.prompt_template = (
            "You are {agent_name}, an AI agent. Use the following tools as needed:\n"
            "{tools}\n"
            "Conversation history:\n"
            "{history}\n"
            "Current input: {input}\n"
            "Respond appropriately."
        )

    def register_tool(self, tool):
        self.tools.append(tool)
        
    def remember(self, message):
        self.conversation_history.append(message)
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history.pop(0)
    
    def generate_response(self, user_input):
        tools_description = "\n".join([f"- {tool['name']}: {tool['description']}" for tool in self.tools])
        history_text = "\n".join(self.conversation_history)
        
        prompt = self.prompt_template.format(
            agent_name=self.name,
            tools=tools_description,
            history=history_text,
            input=user_input
        )
        
        response = self.model.generate_text(prompt)
        self.remember(f"User: {user_input}")
        self.remember(f"{self.name}: {response}")
        
        return response
    
    def reAct(self, user_input):
        # Here you would implement the logic to parse the response for tool usage
        # and handle the tool invocation and results.
        if self.parser and self.tools:
            # Execute generate response in a loop until a final answer is reached
            response = self.generate_response(user_input)
            parsed_response = self.parser.parse(response) ## parsed response is a dict {"InvokeTool": "tool_name", "parameters": {...}} or {"FinalAnswer": "answer"} or {"RequestMoreInfo": "info"}
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
            action = parsed_response.get("action")
            if action == "InvokeTool":
                tool_name = parsed_response["parameters"].get("tool_name")
                tool = next((t for t in self.tools if t['name'] == tool_name), None)
                if tool:
                    tool_result = tool['function'](**parsed_response.get("parameters", {}))
                    self.remember(f"Tool Result: {tool_result}")
                    self.conversation_history.append(f"Tool Result: {tool_result}") 
                    # Generate a new response based on the tool result
                    response = self.generate_response(f"Tool Result: {tool_result}")
                    parsed_response = self.parser.parse(response)
            elif action == "FinalAnswer" or action == "RequestMoreInfo" or action == "NeedApproval":
                return parsed_response.get("content")
            else:
                return "I'm not sure how to proceed. Could you please clarify?"
            # Handle tool invocation and results based on parsed_response
            # This is a placeholder for actual implementation
            print(f"Parsed Response: {parsed_response}")

        return response