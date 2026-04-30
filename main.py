"""
main.py – Punto de entrada del programa de Control de Stock
"""
import database as db
from app import StockApp

if __name__ == "__main__":
    db.init_db()
    app = StockApp()
    app.mainloop()
