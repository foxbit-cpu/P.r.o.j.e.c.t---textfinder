import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import re
from search_engine import search_files

class TextFinder:
    def __init__(self, root):
        self.root = root
        root.title("TextFinder - Search Text in Files")
        root.geometry("900x700")

        # Верхняя панель выбора папки и поиска
        top = tk.Frame(root)
        top.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(top, text="Folder:").pack(side=tk.LEFT)
        self.folder_var = tk.StringVar()
        tk.Entry(top, textvariable=self.folder_var, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Browse...", command=self.select_folder).pack(side=tk.LEFT)

        tk.Label(top, text="Search:").pack(side=tk.LEFT, padx=(20,5))
        self.query_var = tk.StringVar()
        self.query_entry = tk.Entry(top, textvariable=self.query_var, width=30)
        self.query_entry.pack(side=tk.LEFT, padx=5)
        self.query_entry.bind("<Return>", lambda e: self.start_search())

        self.search_btn = tk.Button(top, text="Find", command=self.start_search)
        self.search_btn.pack(side=tk.LEFT, padx=5)

        # Чекбокс "Только целые слова"
        self.whole_word_var = tk.BooleanVar()
        chk = tk.Checkbutton(top, text="Whole words only", variable=self.whole_word_var)
        chk.pack(side=tk.LEFT, padx=10)

        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)

        # Таблица результатов
        self.tree = ttk.Treeview(root, columns=("file", "location", "size"), show="headings")
        self.tree.heading("file", text="File")
        self.tree.heading("location", text="Location")
        self.tree.heading("size", text="Size (bytes)")
        self.tree.column("size", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Панель предпросмотра (нижняя)
        preview_frame = tk.LabelFrame(root, text="Quick Preview (click on any file)")
        preview_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=(0,10))
        self.preview_text = tk.Text(preview_frame, height=8, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Статусная строка
        self.status = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.folder = None

        # Привязка событий
        self.tree.bind("<<TreeviewSelect>>", self.show_preview)
        self.tree.bind("<Double-1>", self.open_file)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder = folder
            self.folder_var.set(folder)

    def start_search(self):
        if not self.folder:
            messagebox.showerror("Error", "Please select a folder.")
            return
        query = self.query_var.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter text to search.")
            return

        for row in self.tree.get_children():
            self.tree.delete(row)
        self.preview_text.delete(1.0, tk.END)
        self.search_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status.config(text="Searching...")

        whole_word = self.whole_word_var.get()
        threading.Thread(target=self.search_thread, args=(self.folder, query, whole_word), daemon=True).start()

    def search_thread(self, folder, query, whole_word):
        results = search_files(folder, query, whole_word=whole_word)
        self.root.after(0, self.show_results, results)

    def show_results(self, results):
        self.progress.stop()
        self.search_btn.config(state=tk.NORMAL)
        for filepath, size in results:
            dirname, filename = os.path.split(filepath)
            self.tree.insert("", "end", values=(filename, dirname, size))
        self.status.config(text=f"Found in {len(results)} files.")
        if not results:
            messagebox.showinfo("Result", "No matches found.")

    def show_preview(self, event):
        """Показывает первые 2000 символов выбранного файла в нижней панели"""
        selected = self.tree.selection()
        if not selected:
            return
        filename = self.tree.item(selected[0], "values")[0]
        location = self.tree.item(selected[0], "values")[1]
        full_path = os.path.join(location, filename)

        content = ""
        try:
            if full_path.lower().endswith('.txt'):
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(2000)
            elif full_path.lower().endswith('.docx'):
                import docx2txt
                content = docx2txt.process(full_path)[:2000]
            elif full_path.lower().endswith('.pdf'):
                import PyPDF2
                with open(full_path, 'rb') as pdf:
                    reader = PyPDF2.PdfReader(pdf)
                    text = ""
                    for page in reader.pages[:2]:
                        text += page.extract_text()
                    content = text[:2000]
            else:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(2000)
        except Exception as e:
            content = f"Could not read file: {e}"

        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, content)

    def open_file(self, event):
        """Открыть файл в родной программе (двойной клик)"""
        selected = self.tree.selection()
        if not selected:
            return
        filename = self.tree.item(selected[0], "values")[0]
        location = self.tree.item(selected[0], "values")[1]
        full_path = os.path.join(location, filename)
        try:
            os.startfile(full_path)
        except AttributeError:
            import subprocess
            subprocess.call(('open', full_path))

    def show_context_menu(self, event):
        """Контекстное меню по правой кнопке мыши"""
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Preview with highlight", command=self.open_preview_window)
            menu.post(event.x_root, event.y_root)

    def open_preview_window(self):
        """Открывает новое окно с полным текстом файла и подсветкой искомого слова"""
        selected = self.tree.selection()
        if not selected:
            return
        filename = self.tree.item(selected[0], "values")[0]
        location = self.tree.item(selected[0], "values")[1]
        full_path = os.path.join(location, filename)
        query = self.query_var.get().strip()
        if not query:
            messagebox.showinfo("Info", "No search term to highlight.")
            return

        # Загружаем весь текст файла
        content = ""
        try:
            if full_path.lower().endswith('.txt'):
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            elif full_path.lower().endswith('.docx'):
                import docx2txt
                content = docx2txt.process(full_path)
            elif full_path.lower().endswith('.pdf'):
                import PyPDF2
                with open(full_path, 'rb') as pdf:
                    reader = PyPDF2.PdfReader(pdf)
                    text_parts = [page.extract_text() for page in reader.pages]
                    content = "\n".join(text_parts)
            else:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
        except Exception as e:
            content = f"Error reading file: {e}"

        # Создаём окно предпросмотра
        preview_win = tk.Toplevel(self.root)
        preview_win.title(f"Preview: {filename}")
        preview_win.geometry("800x600")

        text_widget = tk.Text(preview_win, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = tk.Scrollbar(preview_win, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        text_widget.insert(tk.END, content)
        text_widget.tag_configure("highlight", background="yellow", foreground="black")

        # Подсветка с учётом режима целых слов (через re)
        if self.whole_word_var.get():
            pattern = r'\b' + re.escape(query) + r'\b'
            # Ищем все совпадения в тексте (регистронезависимо)
            for match in re.finditer(pattern, content, re.IGNORECASE):
                start_char = match.start()
                end_char = match.end()
                # Переводим позиции символов в индексы для tkinter
                start_index = text_widget.index(f"1.0 + {start_char} chars")
                end_index = text_widget.index(f"1.0 + {end_char} chars")
                text_widget.tag_add("highlight", start_index, end_index)
        else:
            start = "1.0"
            while True:
                start = text_widget.search(query, start, tk.END, nocase=True)
                if not start:
                    break
                end = f"{start}+{len(query)}c"
                text_widget.tag_add("highlight", start, end)
                start = end

        text_widget.mark_set(tk.INSERT, "1.0")
        text_widget.see("1.0")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextFinder(root)
    root.mainloop()