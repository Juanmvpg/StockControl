"""
main.py – Punto de entrada del programa de Control de Stock
"""
import database as db
from app import StockApp
import logging
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    log_dir = Path(sys.executable).parent
else:
    log_dir = Path(__file__).parent

logging.basicConfig(
    filename=log_dir / 'errores_app.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    db.init_db()
    app = StockApp()
    app.mainloop()
