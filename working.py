from fastapi import FastAPI, Path, Query, HTTPException, Response, status
from typing import Optional
import sqlite3, json
from datetime import datetime  
from dateutil.relativedelta import relativedelta  

app = FastAPI()

@app.get("/")
def home():
    return {"Data": "Testing"}

@app.get("/get-details")
def get_details(*, name: str, LastName: str):
    con = sqlite3.connect("telephones.db")
    cur = con.cursor()
    cur.execute("select * from telephones where Name=? AND LastName=?", (name,LastName))
    data = cur.fetchall()
    cur.close()
    con.close()

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    else:
        columns = [col[0] for col in cur.description]
        data = [dict(zip(columns, row)) for row in data]
        return Response(content=json.dumps(data), media_type="application/json")
    
@app.post("/create-person")
def create_person(Team: str, Name: str, LastName: str, S_N: str, CurrIMEI: str, Orderdate: str, WarrPerriod: int, OldIMEI: Optional[str]=None, WarrEndDate: Optional[str]=None, IMEI2: Optional[str]=None ):
    con = sqlite3.connect("telephones.db")
    cur = con.cursor()
    cur.execute("CREATE table IF NOT EXISTS  telephones(Team, Name, LastName, S_N, CurrIMEI, Orderdate, WarrEndDate, OldIMEI, IMEI2, WarrPerriod)")
    cur.execute("select Name from telephones where Name=? AND LastName=?", (Name,LastName))
    data = cur.fetchall()
    if not data:
        WarrEndDate = datetime.strptime(Orderdate, "%Y-%m-%d") + relativedelta(years=WarrPerriod)  
        data = [(Team, Name, LastName, S_N, CurrIMEI, Orderdate, WarrEndDate, OldIMEI, IMEI2, WarrPerriod)]
        cur.executemany("INSERT INTO telephones VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
        con.commit()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name already exists.")
    con.close()
    return {"Success":"Data created!"}

@app.put("/update-person")
def update_person(
    Name: str, 
    LastName: str, 
    S_N: str, 
    CurrIMEI: str, 
    Orderdate: str, 
    Team: Optional[str]=None,
    WarrPerriod: Optional[int]=None, 
    OldIMEI: Optional[str]=None, 
    IMEI2: Optional[str]=None ):
    con = sqlite3.connect("telephones.db")
    cur = con.cursor()
    cur.execute("select Name, LastName from telephones where Name=? AND LastName=?", (Name,LastName))
    data = cur.fetchall()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provided Name and Last Name does not exist!.")
    else:
        if S_N is not None:
            person_to_update = [(S_N, Name, LastName)]
            cur.executemany("UPDATE telephones SET S_N=? WHERE Name=? AND LastName=?", person_to_update)
        if CurrIMEI is not None:
            person_to_update = [(CurrIMEI, Name, LastName)]
            cur.executemany("UPDATE telephones SET CurrIMEI=? WHERE Name=? AND LastName=?", person_to_update)
        if Orderdate is not None:
            WarrEndDate = datetime.strptime(Orderdate, "%Y-%m-%d") + relativedelta(years=WarrPerriod)  
            person_to_update = [(Orderdate, WarrEndDate, Name, LastName)]
            cur.executemany("UPDATE telephones SET Orderdate=?, WarrEndDate=? WHERE Name=? AND LastName=?", person_to_update)
        if Team is not None:
            person_to_update = [(Team, Name, LastName)]
            cur.executemany("UPDATE telephones SET Team=? WHERE Name=? AND LastName=?", person_to_update)
        if WarrPerriod is not None:
            person_to_update = [(WarrPerriod, Name, LastName)]
            cur.executemany("UPDATE telephones SET WarrPerriod=? WHERE Name=? AND LastName=?", person_to_update)
        if OldIMEI is not None:
            person_to_update = [(OldIMEI, Name, LastName)]
            cur.executemany("UPDATE telephones SET OldIMEI=? WHERE Name=? AND LastName=?", person_to_update)
        #if WarrEndDate is not None:
        #    person_to_update = [(WarrEndDate, Name, LastName)]
        #    cur.executemany("UPDATE telephones SET WarrEndDate=? WHERE Name=? AND LastName=?", person_to_update)
        if IMEI2 is not None:
            person_to_update = [(IMEI2, Name, LastName)]
            cur.executemany("UPDATE telephones SET SIMEI2_N=? WHERE Name=? AND LastName=?", person_to_update)

    con.commit()
    con.close()
    return {"Success":"Data updated!"}

@app.delete("/delete-person")
def delete_person(Name: str, LastName: str):
    con = sqlite3.connect("telephones.db")
    cur = con.cursor()
    cur.execute("select Name, LastName from telephones where Name=? AND LastName=?", (Name,LastName))
    data = cur.fetchall()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided Name and Last Name does not exist!.")
    else:
        person_to_delete = [(Name, LastName)]
        cur.executemany("DELETE FROM telephones WHERE Name=? AND LastName=?", person_to_delete)
        con.commit()

    con.close()
    return {"Success":"Data deleted!"}

@app.get("/about")
def about():
    return {"Tomo PIRMASIS API!!!!!"}