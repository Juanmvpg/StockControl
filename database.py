"""
database.py – Capa de acceso a datos (SQLite)
"""
import sqlite3
import csv
from pathlib import Path
import sys

if getattr(sys, 'frozen', False):
    # La aplicación se está ejecutando desde un ejecutable (PyInstaller)
    base_dir = Path(sys.executable).parent
else:
    # La aplicación se está ejecutando desde script
    base_dir = Path(__file__).parent

DB_FILE = base_dir / "stock.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Crea las tablas si no existen y aplica migraciones."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS productos (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo    TEXT UNIQUE NOT NULL,
                nombre    TEXT NOT NULL,
                categoria TEXT DEFAULT '',
                marca     TEXT DEFAULT '',
                stock     REAL DEFAULT 0.0,
                minimo    REAL DEFAULT 0.0,
                precio    REAL DEFAULT 0.0,
                por_peso  INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS movimientos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL REFERENCES productos(id),
                tipo        TEXT NOT NULL CHECK(tipo IN ('entrada','salida')),
                cantidad    REAL NOT NULL,
                fecha       TEXT DEFAULT (strftime('%Y-%m-%d %H:%M', 'now', 'localtime')),
                nota        TEXT DEFAULT '',
                forzado     INTEGER DEFAULT 0,
                saldado     INTEGER DEFAULT 0,
                grupo_id    TEXT DEFAULT NULL
            );

            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            );
        """)
        # Migraciones: agregar columnas si no existen (SQLite no tiene IF NOT EXISTS para columnas)
        cols = {row[1] for row in conn.execute("PRAGMA table_info(movimientos)").fetchall()}
        if "forzado" not in cols:
            conn.execute("ALTER TABLE movimientos ADD COLUMN forzado INTEGER DEFAULT 0")
        if "saldado" not in cols:
            conn.execute("ALTER TABLE movimientos ADD COLUMN saldado INTEGER DEFAULT 0")
        if "precio" not in cols:
            conn.execute("ALTER TABLE movimientos ADD COLUMN precio REAL DEFAULT NULL")
        if "grupo_id" not in cols:
            conn.execute("ALTER TABLE movimientos ADD COLUMN grupo_id TEXT DEFAULT NULL")

        cols_prod = {row[1] for row in conn.execute("PRAGMA table_info(productos)").fetchall()}
        if "marca" not in cols_prod:
            conn.execute("ALTER TABLE productos ADD COLUMN marca TEXT DEFAULT ''")
        if "por_peso" not in cols_prod:
            conn.execute("ALTER TABLE productos ADD COLUMN por_peso INTEGER DEFAULT 0")
        if "nota" not in cols_prod:
            conn.execute("ALTER TABLE productos ADD COLUMN nota TEXT DEFAULT ''")
        if "activo" not in cols_prod:
            conn.execute("ALTER TABLE productos ADD COLUMN activo INTEGER DEFAULT 1")
        if "precio_costo" not in cols_prod:
            conn.execute("ALTER TABLE productos ADD COLUMN precio_costo REAL DEFAULT 0.0")


# ──────────────────────────────────────────────
#  Productos
# ──────────────────────────────────────────────

def get_productos(filtro=""):
    """Devuelve todos los productos; filtra por código/nombre/categoría."""
    with get_connection() as conn:
        if filtro:
            like = f"%{filtro}%"
            rows = conn.execute(
                "SELECT * FROM productos WHERE activo=1 AND (codigo LIKE ? OR nombre LIKE ? OR categoria LIKE ? OR marca LIKE ?) ORDER BY nombre",
                (like, like, like, like)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM productos WHERE activo=1 ORDER BY nombre").fetchall()
    return [dict(r) for r in rows]


def get_producto_by_id(pid):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone()
    return dict(row) if row else None


def crear_producto(codigo, nombre, categoria, marca, stock, minimo, precio, por_peso=0, precio_costo=0.0):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO productos (codigo,nombre,categoria,marca,stock,minimo,precio,por_peso,precio_costo) VALUES (?,?,?,?,?,?,?,?,?)",
            (codigo, nombre, categoria, marca, stock, minimo, precio, por_peso, precio_costo)
        )



def upsert_producto(codigo, nombre, categoria, marca, stock, minimo, precio, por_peso=0, precio_costo=0.0):
    """
    Si el código existe (o si código está vacío y el nombre existe), 
    actualiza sus datos (excepto el stock, a menos que se quiera sobreescribir).
    Devuelve (True, []) si es nuevo o (False, cambios_list) si se actualizó.
    """
    with get_connection() as conn:
        row = None
        # Intentar buscar por código si lo tenemos
        if codigo:
            row = conn.execute("SELECT * FROM productos WHERE codigo=?", (codigo,)).fetchone()
            
        # Si no lo encontramos por código (o no vino código), intentar por nombre, marca y categoría exactos
        if not row:
            row = conn.execute(
                "SELECT * FROM productos WHERE nombre=? AND IFNULL(marca, '')=? AND IFNULL(categoria, '')=?", 
                (nombre, marca, categoria)
            ).fetchone()
            
        if row:
            cambios = []
            
            # Comparar cambios
            if row["nombre"] != nombre: 
                cambios.append(f"Nombre: {row['nombre']} -> {nombre}")
            if (row["categoria"] or "") != categoria: 
                cambios.append(f"Categoría: {row['categoria']} -> {categoria}")
            if (row["marca"] or "") != marca: 
                cambios.append(f"Marca: {row['marca']} -> {marca}")
            if float(row["minimo"] or 0) != float(minimo): 
                cambios.append(f"Mínimo: {row['minimo']} -> {minimo}")
            if float(row["precio"] or 0) != float(precio): 
                cambios.append(f"Precio: {row['precio']} -> {precio}")
            if float(row["precio_costo"] or 0) != float(precio_costo):
                cambios.append(f"Costo: {row['precio_costo']} -> {precio_costo}")
            if int(row["por_peso"] or 0) != int(por_peso): 
                cambios.append(f"Por peso: {'Sí' if por_peso else 'No'}")
            
            if row["activo"] == 0:
                cambios.append("Estado: [RECUPERADO DE PAPELERA]")

            if codigo and row["codigo"] != codigo:
                cambios.insert(0, f"Código: {row['codigo']} -> {codigo}")
                conn.execute(
                    "UPDATE productos SET codigo=?, nombre=?, categoria=?, marca=?, minimo=?, precio=?, precio_costo=?, por_peso=?, activo=1 WHERE id=?",
                    (codigo, nombre, categoria, marca, minimo, precio, precio_costo, por_peso, row["id"])
                )
            else:
                conn.execute(
                    "UPDATE productos SET nombre=?, categoria=?, marca=?, minimo=?, precio=?, precio_costo=?, por_peso=?, activo=1 WHERE id=?",
                    (nombre, categoria, marca, minimo, precio, precio_costo, por_peso, row["id"])
                )
            return False, cambios  # (fue un update, lista_de_cambios)
        else:
            # Producto nuevo: Generar código si no viene
            if not codigo:
                max_id_row = conn.execute("SELECT MAX(id) as mx FROM productos").fetchone()
                siguiente = (max_id_row["mx"] or 0) + 1
                codigo = f"PRD-{siguiente:04d}"
                
            # Insertamos todo
            conn.execute(
                "INSERT INTO productos (codigo,nombre,categoria,marca,stock,minimo,precio,precio_costo,por_peso) VALUES (?,?,?,?,?,?,?,?,?)",
                (codigo, nombre, categoria, marca, stock, minimo, precio, precio_costo, por_peso)
            )
            return True, []   # (fue un insert, sin_cambios)



def actualizar_producto(pid, codigo, nombre, categoria, marca, stock, minimo, precio, por_peso=0, precio_costo=0.0):
    with get_connection() as conn:
        conn.execute(
            "UPDATE productos SET codigo=?,nombre=?,categoria=?,marca=?,stock=?,minimo=?,precio=?,precio_costo=?,por_peso=? WHERE id=?",
            (codigo, nombre, categoria, marca, stock, minimo, precio, precio_costo, por_peso, pid)
        )

def actualizar_productos_masivo(ids, campos_actualizar):
    if not ids or not campos_actualizar:
        return 0
        
    set_clauses = []
    values = []
    
    for k, v in campos_actualizar.items():
        set_clauses.append(f"{k}=?")
        values.append(v)
        
    set_string = ", ".join(set_clauses)
    placeholders = ",".join(["?"] * len(ids))
    values.extend(ids)
    
    query = f"UPDATE productos SET {set_string} WHERE id IN ({placeholders})"
    
    with get_connection() as conn:
        cur = conn.execute(query, tuple(values))
        return cur.rowcount

def actualizar_nota_producto(pid, nota):
    with get_connection() as conn:
        conn.execute("UPDATE productos SET nota=? WHERE id=?", (nota, pid))

def aplicar_aumento_masivo(valor, tipo_aumento, categoria=None, marca=None, ids=None):
    """
    valor: float (monto o porcentaje)
    tipo_aumento: 'porcentaje' o 'fijo'
    Devuelve lista de tuplas: (nombre_producto, precio_anterior, precio_nuevo)
    """
    cambios = []
    with get_connection() as conn:
        # Armar consulta SELECT para obtener los productos a modificar
        query_sel = "SELECT id, nombre, precio FROM productos WHERE 1=1"
        params = []
        
        if ids is not None and len(ids) > 0:
            placeholders = ",".join(["?"] * len(ids))
            query_sel += f" AND id IN ({placeholders})"
            params.extend(ids)
        else:
            if categoria and categoria != "Cualquiera":
                query_sel += " AND categoria=?"
                params.append(categoria)
            if marca and marca != "Cualquiera":
                query_sel += " AND marca=?"
                params.append(marca)
                
        productos_afectados = conn.execute(query_sel, tuple(params)).fetchall()
        
        for p in productos_afectados:
            pid = p["id"]
            nombre = p["nombre"]
            precio_ant = p["precio"]
            
            if tipo_aumento == "porcentaje":
                precio_nuevo = precio_ant + (precio_ant * valor / 100.0)
                tipo_str = "Aumento" if valor >= 0 else "Baja"
                nota_mov = f"{tipo_str} {abs(valor)}%, precio anterior: ${precio_ant:,.2f}, precio actual: ${precio_nuevo:,.2f}"
            else:
                precio_nuevo = precio_ant + valor
                tipo_str = "Aumento" if valor >= 0 else "Baja"
                nota_mov = f"{tipo_str} ${abs(valor):,.2f}, precio anterior: ${precio_ant:,.2f}, precio actual: ${precio_nuevo:,.2f}"
                
            # Actualizar producto
            conn.execute("UPDATE productos SET precio=? WHERE id=?", (precio_nuevo, pid))
            
            # Registrar en historial (movimientos) como cantidad 0 para dejar rastro de cambio de precio
            conn.execute(
                "INSERT INTO movimientos (producto_id, tipo, cantidad, nota, forzado, precio, grupo_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (pid, "entrada", 0, nota_mov, 0, precio_nuevo, None)
            )
            
            cambios.append((nombre, precio_ant, precio_nuevo))
            
        conn.commit()
    return cambios

def registrar_salida_multi(carrito_items, grupo_id=None, iter_precio=None):
    """
    carrito_items: lista de dicts con pid (item id), prod, cant, nota.
    Deduce el stock y registra el movimiento de tipo 'salida' con grupo_id y precio.
    """
    movs = []
    with get_connection() as conn:
        for idx, item in enumerate(carrito_items):
            pid = item["prod"]["id"]
            cant = item["cant"]
            nota = item["nota"]
            precio = None
            if iter_precio is not None and idx < len(iter_precio):
                precio = iter_precio[idx]

            conn.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cant, pid))
            cur = conn.execute(
                "INSERT INTO movimientos (producto_id, tipo, cantidad, nota, grupo_id, precio) VALUES (?, ?, ?, ?, ?, ?)",
                (pid, "salida", cant, nota, grupo_id, precio)
            )
            movs.append(cur.lastrowid)
        conn.commit()
    return movs

def get_incremental_order():
    """Obtiene el próximo número de orden incremental y lo guarda en configuración."""
    import datetime
    now = datetime.datetime.now()
    meses_abrev = ["En", "Fe", "MA", "Ab", "Ma", "JU", "Ju", "Ag", "Se", "Oc", "No", "Di"]
    mes_str = meses_abrev[now.month - 1]
    dia_str = f"{now.day:02d}"

    with get_connection() as conn:
        # Check current value
        row = conn.execute("SELECT valor FROM configuracion WHERE clave = 'ultimo_orden'").fetchone()
        if not row:
            conn.execute("INSERT INTO configuracion (clave, valor) VALUES ('ultimo_orden', '1')")
            siguiente = 1
        else:
            siguiente = int(row["valor"]) + 1
            conn.execute("UPDATE configuracion SET valor = ? WHERE clave = 'ultimo_orden'", (str(siguiente),))
        conn.commit()
        return f"Venta #{dia_str}{siguiente:04d}-{mes_str}"

# ──────────────────────────────────────────────
#  Importación Masiva (Merge)
# ──────────────────────────────────────────────




def eliminar_producto(pid):
    with get_connection() as conn:
        prod = conn.execute("SELECT nombre FROM productos WHERE id=?", (pid,)).fetchone()
        if prod:
            nombre = prod["nombre"]
            # En lugar de eliminar el historial asociado, insertamos un movimiento de registro
            conn.execute(
                "INSERT INTO movimientos (producto_id,tipo,cantidad,nota,forzado,precio,grupo_id) VALUES (?,?,?,?,?,?,?)",
                (pid, "salida", 0, f"Producto Eliminado: {nombre}", 1, None, None)
            )
        # Soft-delete: en vez de DELETE, lo marcamos como inactivo.
        conn.execute("UPDATE productos SET activo = 0 WHERE id=?", (pid,))


# ──────────────────────────────────────────────
#  Movimientos
# ──────────────────────────────────────────────

def registrar_movimiento(producto_id, tipo, cantidad, nota="", forzar=False, precio_total=None, grupo_id=None):
    """Registra un movimiento y actualiza el stock.
    Si forzar=True, ignora el control de stock insuficiente."""
    with get_connection() as conn:
        if tipo == "salida" and not forzar:
            row = conn.execute("SELECT stock FROM productos WHERE id=?", (producto_id,)).fetchone()
            if not row or row["stock"] < cantidad:
                raise ValueError("Stock insuficiente para realizar la salida.")

        delta = cantidad if tipo == "entrada" else -cantidad
        conn.execute(
            "INSERT INTO movimientos (producto_id,tipo,cantidad,nota,forzado,precio,grupo_id) VALUES (?,?,?,?,?,?,?)",
            (producto_id, tipo, cantidad, nota, 1 if forzar else 0, precio_total, grupo_id)
        )
        conn.execute("UPDATE productos SET stock=stock+? WHERE id=?", (delta, producto_id))


def toggle_saldado(mov_id):
    """Alterna el estado 'saldado' de un movimiento."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE movimientos SET saldado = CASE WHEN saldado=1 THEN 0 ELSE 1 END WHERE id=?",
            (mov_id,)
        )


def get_movimientos(producto_id=None, limit=500):
    with get_connection() as conn:
        if producto_id:
            rows = conn.execute(
                """SELECT m.id, m.producto_id, m.tipo, m.cantidad, m.fecha,
                          m.nota, m.forzado, m.saldado, m.precio, m.grupo_id, p.nombre, p.codigo
                   FROM movimientos m JOIN productos p ON m.producto_id=p.id
                   WHERE m.producto_id=?
                   ORDER BY m.id DESC LIMIT ?""",
                (producto_id, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT m.id, m.producto_id, m.tipo, m.cantidad, m.fecha,
                          m.nota, m.forzado, m.saldado, m.precio, m.grupo_id, p.nombre, p.codigo
                   FROM movimientos m JOIN productos p ON m.producto_id=p.id
                   ORDER BY m.id DESC LIMIT ?""",
                (limit,)
            ).fetchall()
    return [dict(r) for r in rows]


def get_categorias():
    """Devuelve lista de categorías únicas no vacías más las personalizadas en configuración."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT categoria FROM productos WHERE categoria != '' ORDER BY categoria"
        ).fetchall()
        
        custom_row = conn.execute("SELECT valor FROM configuracion WHERE clave='custom_categorias'").fetchone()

    cats_db = [r["categoria"] for r in rows]
    cats_custom = []
    if custom_row and custom_row["valor"]:
        cats_custom = [c.strip() for c in custom_row["valor"].split('|') if c.strip()]
        
    todas = set(cats_db + cats_custom)
    return sorted(list(todas))


def get_marcas():
    """Devuelve lista de marcas únicas no vacías más las personalizadas en configuración."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT marca FROM productos WHERE marca != '' AND marca IS NOT NULL ORDER BY marca"
        ).fetchall()
        
        custom_row = conn.execute("SELECT valor FROM configuracion WHERE clave='custom_marcas'").fetchone()

    marcas_db = [r["marca"] for r in rows]
    marcas_custom = []
    if custom_row and custom_row["valor"]:
        marcas_custom = [m.strip() for m in custom_row["valor"].split('|') if m.strip()]
        
    todas = set(marcas_db + marcas_custom)
    return sorted(list(todas))


# ──────────────────────────────────────────────
#  Configuración
# ──────────────────────────────────────────────

def get_config(clave, default=None):
    with get_connection() as conn:
        row = conn.execute("SELECT valor FROM configuracion WHERE clave=?", (clave,)).fetchone()
    return row["valor"] if row else default


def set_config(clave, valor):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO configuracion (clave, valor) VALUES (?,?) "
            "ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor",
            (clave, str(valor))
        )


def aplicar_minimo_defecto(minimo):
    """Aplica un stock mínimo a todos los productos que aún tienen minimo=0."""
    with get_connection() as conn:
        conn.execute("UPDATE productos SET minimo=? WHERE minimo=0", (minimo,))
        return conn.execute("SELECT changes()").fetchone()[0]


def get_stock_bajo():
    """Productos cuyo stock está por debajo del mínimo."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM productos WHERE stock < minimo AND activo = 1 ORDER BY nombre"
        ).fetchall()
    return [dict(r) for r in rows]


# ──────────────────────────────────────────────
#  Exportación
# ──────────────────────────────────────────────

def exportar_excel(filepath):
    import pandas as pd
    productos = get_productos()
    if not productos:
        return 0
    df = pd.DataFrame(productos)
    cols_to_drop = [col for col in ['id', 'activo'] if col in df.columns]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
    
    df = df.rename(columns={
        'codigo': 'Código',
        'nombre': 'Nombre',
        'categoria': 'Categoría',
        'marca': 'Marca',
        'stock': 'Stock',
        'minimo': 'Stock Mínimo',
        'precio': 'Precio Venta',
        'precio_costo': 'Precio Costo',
        'por_peso': 'Se vende por peso',
        'nota': 'Nota'
    })
    
    df.to_excel(filepath, index=False)
    return len(productos)


def vaciar_movimientos():
    """Elimina todos los movimientos del historial. Retorna la cantidad borrada."""
    with get_connection() as conn:
        n = conn.execute("SELECT COUNT(*) FROM movimientos").fetchone()[0]
        conn.execute("DELETE FROM movimientos")
        conn.execute("UPDATE configuracion SET valor = '0' WHERE clave = 'ultimo_orden'")
    return n
