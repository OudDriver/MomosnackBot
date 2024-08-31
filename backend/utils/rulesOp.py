import json
import re
import discord

def load_rules():
    with open("rules.json") as f:
        return json.loads(f.read())

def save_rules(ruleDict):
    with open("rules.json", "w") as f:
        finalJSON = json.dumps(ruleDict)
        finalJSON = re.sub(r"\\\\", r"\\", finalJSON)
        f.write(finalJSON)
        
async def rule_trigger(message: discord.message.Message):
    regexContent = re.finditer(r"rule-\d+", message.content, re.IGNORECASE)
    if re.search(r"rule-\d+", message.content, re.IGNORECASE): 
        RULE_DICT = load_rules()
            
        ruleMessage = ""
        for rule in regexContent:
            ruleString = rule.group()
            for key in RULE_DICT:
                if ruleString in key:
                    ruleMessage += f"{RULE_DICT[ruleString]}\n\n"
                    
        if ruleMessage != "" :
            await message.reply(ruleMessage)