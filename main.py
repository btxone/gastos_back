from fastapi import FastAPI, HTTPException
import pandas as pd
from pydantic import BaseModel
from datetime import datetime
import os
import pytz
import logging

# Configurar el logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

class Expense(BaseModel):
    price: float
    description: str
    excel_name: str  # Nuevo campo para el nombre del archivo Excel

@app.post("/add-expense/")
def add_expense(expense: Expense):
    uruguay_zone = pytz.timezone('America/Montevideo')
    now_in_uruguay = datetime.now(uruguay_zone).replace(tzinfo=None)
    
    # Construir el nombre del archivo con base en el input del usuario
    excel_file = f"{expense.excel_name}.xlsx"

    new_data = pd.DataFrame({
        "Date": [now_in_uruguay],
        "Price": [expense.price],
        "Description": [expense.description]
    })

    try:
        if not os.path.exists(excel_file):
            new_data.to_excel(excel_file, index=False)
        else:
            with pd.ExcelWriter(excel_file, mode='a', engine="openpyxl", if_sheet_exists='overlay') as writer:
                new_data.to_excel(writer, startrow=writer.sheets['Sheet1'].max_row, index=False, header=False)
        
        logger.info(f"Gasto agregado en {excel_file}: {expense.price} - {expense.description}")
    except Exception as e:
        logger.error(f"Error al agregar gasto en {excel_file}: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar el gasto")
    
    return {"message": "Expense added successfully"}
