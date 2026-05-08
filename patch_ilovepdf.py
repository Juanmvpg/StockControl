import sys
import re

with open(r'c:\Users\gian9\.gemini\antigravity\scratch\stock-control\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

ilovepdf_code = """
class ILovePdfDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Convertidor PDF a Excel (iLovePDF)")
        self.geometry("500x350")
        self.configure(bg=BG)
        self.transient(parent)
        self.grab_set()
        
        # Check API Key
        self.api_key = db.get_config("ilovepdf_api_key", "")
        
        lbl_title = tk.Label(self, text="Conversión Inteligente con iLovePDF", bg=BG, fg=TEXT, font=("Segoe UI", 12, "bold"))
        lbl_title.pack(pady=10)
        
        self.frame_key = tk.Frame(self, bg=BG)
        self.frame_key.pack(fill="x", padx=20, pady=5)
        
        tk.Label(self.frame_key, text="Para usar este servicio gratuito necesitas una Clave API Pública.", bg=BG, fg=TEXT_DIM, wraplength=450).pack(anchor="w")
        
        link = tk.Label(self.frame_key, text="1. Haz clic aquí para registrarte y obtener tu clave gratis", fg=ACCENT, bg=BG, cursor="hand2")
        link.pack(anchor="w", pady=(5,0))
        link.bind("<Button-1>", lambda e: __import__('webbrowser').open("https://developer.ilovepdf.com/signup"))
        
        key_box = tk.Frame(self.frame_key, bg=BG)
        key_box.pack(fill="x", pady=5)
        tk.Label(key_box, text="Public Key:", bg=BG, fg=TEXT).pack(side="left")
        self.entry_key = entry(key_box, width=40)
        self.entry_key.pack(side="left", padx=5)
        self.entry_key.insert(0, self.api_key)
        
        styled_btn(key_box, "Guardar", self.guardar_key, color=SUCCESS).pack(side="left")
        
        # Convert Area
        self.frame_convert = tk.Frame(self, bg=BG)
        self.frame_convert.pack(fill="both", expand=True, padx=20, pady=10)
        
        if not self.api_key:
            self.frame_convert.pack_forget()
            
        tk.Label(self.frame_convert, text="Selecciona un PDF de tu proveedor para convertir a Excel:", bg=BG, fg=TEXT).pack(anchor="w", pady=5)
        
        btn_seleccionar = styled_btn(self.frame_convert, "📂 Seleccionar PDF y Convertir", self.convertir_pdf, color=ACCENT)
        btn_seleccionar.pack(pady=10)
        
        self.lbl_status = tk.Label(self.frame_convert, text="", bg=BG, fg=TEXT_DIM)
        self.lbl_status.pack(pady=5)
        
    def guardar_key(self):
        k = self.entry_key.get().strip()
        if not k:
            messagebox.showwarning("Error", "Debes ingresar una clave API.", parent=self)
            return
        db.set_config("ilovepdf_api_key", k)
        self.api_key = k
        self.frame_convert.pack(fill="both", expand=True, padx=20, pady=10)
        messagebox.showinfo("Guardado", "Clave guardada correctamente.", parent=self)
        
    def convertir_pdf(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Seleccionar lista en PDF",
            parent=self
        )
        if not filepath:
            return
            
        savepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            title="Guardar archivo Excel convertido como...",
            initialfile=pathlib.Path(filepath).stem + " - Convertido.xlsx",
            parent=self
        )
        if not savepath:
            return
            
        self.lbl_status.config(text="Subiendo a iLovePDF y procesando... Esto puede tardar unos segundos.", fg=WARNING)
        self.update()
        
        def run_conversion():
            try:
                from pylovepdf.ilovepdf import ILovePdf
                import os
                ilovepdf = ILovePdf(self.api_key, verify_ssl=True)
                task = ilovepdf.new_task('pdfaexcel')
                task.add_file(filepath)
                task.set_output_folder(os.path.dirname(savepath))
                task.execute()
                task.download()
                task.delete_current_task()
                
                # The downloaded file has a specific name depending on the input, we rename it
                # Usually it's the same name but .xlsx
                downloaded_file = os.path.join(os.path.dirname(savepath), pathlib.Path(filepath).stem + ".xlsx")
                if os.path.exists(downloaded_file) and downloaded_file != savepath:
                    if os.path.exists(savepath):
                        os.remove(savepath)
                    os.rename(downloaded_file, savepath)
                
                self.after(0, lambda: self.lbl_status.config(text="¡Conversión exitosa!", fg=SUCCESS))
                self.after(0, lambda: messagebox.showinfo("Listo", f"El archivo Excel ha sido guardado en:\\n{savepath}", parent=self))
            except Exception as e:
                self.after(0, lambda: self.lbl_status.config(text="Error en la conversión.", fg=DANGER))
                self.after(0, lambda: messagebox.showerror("Error", f"Ocurrió un error con iLovePDF:\\n{e}", parent=self))
                
        import threading
        threading.Thread(target=run_conversion, daemon=True).start()
"""

# Insert the dialog before ReporteCapitalDialog
dialog_pos = content.find("class ReporteCapitalDialog")
content = content[:dialog_pos] + ilovepdf_code + "\n" + content[dialog_pos:]

# Add to Datos Menu
datos_menu_pos = content.find("menu_datos.add_command(label=\"📊  Comparador de Listas\"")
new_menu_item = "menu_datos.add_command(label=\"📄  Convertir PDF a Excel\", command=self._abrir_ilovepdf)\n        "
content = content[:datos_menu_pos] + new_menu_item + content[datos_menu_pos:]

# Add the function _abrir_ilovepdf
func_code = """
    def _abrir_ilovepdf(self):
        ILovePdfDialog(self)
"""
func_pos = content.find("def _abrir_dashboard_ventas(self):")
content = content[:func_pos] + func_code + "\n    " + content[func_pos:]

# We need to add PyInstaller hidden import for pylovepdf
# We'll just patch the PyInstaller command in the message

with open(r'c:\Users\gian9\.gemini\antigravity\scratch\stock-control\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated app.py")
