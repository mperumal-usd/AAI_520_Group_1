
class Parser:
    def parse(self, response):
        '''A simple parser that looks for specific keywords in the response.
        '''
        return {"action": "FinalAnswer", "parameters": {}}
    
class XmlParser(Parser):
    def parse(self, response):
        '''A parser that extracts XML tags from the response.
        For example, it looks for <InvokeTool>{"symbol": "AAPL", "step": "financials"}</InvokeTool>
        or <FinalAnswer>answer</FinalAnswer>.
        Returns : a dict with action and parameters. Example:
        {
            "action": "InvokeTool",
            "parameters": {
                "symbol": "AAPL",
                "step": "financials"
            }
        }
        '''
        import re
        pattern = r'<(\w+)>(.*?)</\1>'
        matches = re.findall(pattern, response)
        if matches:
            action, content = matches[0]
            content = content.strip()
            contentJson = {}
            try:
                import json
                contentJson = json.loads(content)
            except:
                contentJson = {"content": content}
                return {"action": action, "parameters": contentJson, "error": "Content is not valid JSON"}
            return {"action": action, "parameters": contentJson}
        return {"action": "FinalAnswer", "parameters": {}}
    
    def  parse_all(self, response):
        '''Parse all XML tags in the response and return a list of dicts.
<NeedApproval>The user wants to know the current price for "AAPL".</NeedApproval>
<Thought>The user is asking for the current price of "AAPL". The "Yahoo Finance Stock Quote" tool can provide this information. I will call this tool with the symbol "AAPL".</Thought>
<InvokeTool>{"name": "Yahoo Finance Stock Quote", "api": "{ \"symbol\": \"AAPL\"}"}</InvokeTool>
        Response : [
        {
            "action": "NeedApproval",
            "parameters": {
                "content": "The user wants to know the current price for \"AAPL\"."
            }
        },
        {
            "action": "Thought",
            "parameters": {
                "content": "The user is asking for the current price of \"AAPL\". The \"Yahoo Finance Stock Quote\" tool can provide this information. I will call this tool with the symbol \"AAPL\"."
            }
        },
        {
            "action": "InvokeTool",
            "parameters": {
                "name": "Yahoo Finance Stock Quote",
                "api": "{ \"symbol\": \"AAPL\"}"
        }
        ]
        '''
        import re
        pattern = r'<(\w+)>(.*?)</\1>'
        matches = re.findall(pattern, response)
        results = []
        for action, content in matches:
            content = content.strip()
            contentJson = {}
            try:
                import json
                contentJson = json.loads(content)
            except:
                contentJson = {"content": content}
                results.append({"action": action, "parameters": contentJson, "error": "Content is not valid JSON"})
                continue
            results.append({"action": action, "parameters": contentJson})
        if not results:
            results.append({"action": "FinalAnswer", "parameters": {}})
        return results  