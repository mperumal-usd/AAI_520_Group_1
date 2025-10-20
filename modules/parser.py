# We'll define first a Parser abstract class
class Parser:
    def parse(self, response): # This is the placeholder of the default method for this class
        # Here's the returned value, which will be a dictionary with an Action value, and a list of dynamic parameters.
        return {"action": "FinalAnswer", "parameters": {}}
# Next, we'll define an XML parser, which inherits from our abstract class Parser.    
class XmlParser(Parser):
    def parse(self, response):
        # A parser that extracts XML tags from the response.
        # For example, it looks for <InvokeTool>{"symbol": "AAPL", "step": "financials"}</InvokeTool>
        # or <FinalAnswer>answer</FinalAnswer>.
        # Returns : a dict with action and parameters. Example:
        # {
        #    "action": "InvokeTool",
        #    "parameters": {
        #        "symbol": "AAPL",
        #        "step": "financials"
        #    }
        #}
        import re
        pattern = r'<(\w+)>(.*?)</\1>' # Defining the regular expression for XML structure
        matches = re.findall(pattern, response) # Identifying all matches of XML
        if matches: # When there are XML matches, we'll separate them and parse their contents
            action, content = matches[0]
            content = content.strip()
            contentJson = {}
            try:
                import json
                contentJson = json.loads(content) # Once parsed, we'll reformat them to JSON
            except:
                contentJson = {"content": content} # If the content is not valid, we'll return the error message with the invalid content text
                return {"action": action, "parameters": contentJson, "error": "Content is not valid JSON"}
            return {"action": action, "parameters": contentJson} # If it was valid, we return the parsed content in JSON format
        return {"action": "FinalAnswer", "parameters": {}} #If there wasn't any XML to begin with, we just return an empty list of parameters
    # Next, we have a specialized parsing for our agent's functionality that will interpret the actions in XML tags and encode them as a list of dictionaries
    def parse_all(self, response):
        import re
        pattern = r'<(\w+)>(.*?)</\1>' # Defining the regular expression for XML structure
        matches = re.findall(pattern, response) # Identifying all matches of XML
        results = [] # Preparing an empty array for the results
        for action, content in matches: # For each detected action (if any),
            content = content.strip()   # we'll parse its contents
            contentJson = {}
            try: # Then, we'll try to convert it to JSON format
                import json
                contentJson = json.loads(content)
            except: # Should any errors occur, we'll return the error message as part of the response
                contentJson = {"content": content}
                results.append({"action": action, "parameters": contentJson, "error": "Content is not valid JSON"})
                continue
            results.append({"action": action, "parameters": contentJson}) # If everything's fine, we'll return the parsed JSON content
        if not results:
            results.append({"action": "FinalAnswer", "parameters": {}}) # If there were no actions, we'll return an empty dictionary
        return results  
    
    def parseTags(self, response):
        '''Agent response parser to extract all TAGS.
            Returns a dictionary with tag names as keys and tag values as values.
        '''
        import re
        pattern = r'<(\w+)>(.*?)</\1>'
        matches = re.findall(pattern, response)
        result = {}
        for tag, value in matches:
                result[tag.lower()] = value.strip() 
        return result