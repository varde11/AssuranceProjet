a = """
{
"vehiculeA": {"point11": "Pare choc droit endommage", "point14": "N'avait pas de clignotant !"}, 
"vehiculeB": {"point11": "Angle arriere droit pare-choc (cote de caisse)", "point14": "Etait sur son telephone !"}
}
"""
import json

b = json.loads(a)
print(b)
print(type(b))
print(b["bjr"])