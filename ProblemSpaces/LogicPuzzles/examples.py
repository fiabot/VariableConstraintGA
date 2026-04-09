examples = {
    "examples": [
        {
            "title": "Murder Mystery", 
            "desc": "Use the clues to find out who killed Mr. Boddy!", 
            "categories":[{"name": "Suspects", "entities": ["Col. Mustard", "Prof. Plum", "Ms. Scarlet", "Mrs. White"], "is_numeric": False, "inc":0}, 
            {"name": "Weapons", "entities": ["Rope", "Knife", "Candlestick", "Wrench", "Revolver"], "is_numeric": False, "inc":0}, 
            {"name": "Time", "entities": ["5pm", "6pm", "7pm", "8pm", "9pm"], "is_numeric": True, "inc":1}
        ]
        }, {
            "title": "Magic Potion", 
            "desc": "Use the clues to determine how to cook up this magical potion", 
            "categories":[
                {"name":"Ingredients", "entities": ["Eye of Newt", "Cobwebs", "Feathers", "Petals"], "is_numeric":False, "inc":0}, 
                {"name":"Preparation", "entities": ["Boiled", "Crushed", "Charred", "Chopped"], "is_numeric":False, "inc":0}, 
                {"name":"Order", "entities": ["1st", "2nd", "3rd", "4th",], "is_numeric":True, "inc":1}, 
                
            ]
        },{
            "title": "School Schedule", 
            "desc": "Help Timmy remember his school schedule", 
            "categories":[
                {"name":"Subject", "entities": ["English", "Math", "Science", "History"], "is_numeric":False, "inc":0}, 
                {"name":"Teacher", "entities": ["Ms. Smith", "Mr. Williams", "Ms. Johnson", "Mr. Brown"], "is_numeric":False, "inc":0}, 
                {"name":"Period", "entities": ["1st", "2nd", "3rd", "4th"], "is_numeric":True, "inc":1}, 
               
            ]
        }
    ]
}