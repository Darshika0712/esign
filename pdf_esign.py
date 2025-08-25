import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import fitz
from PIL import Image, ImageTk
import io
import os
from datetime import datetime
import time

class SignatureDialog(simpledialog.Dialog):
    def __init__(self, parent, sig_type="text", initial=""):
        self.sig_type = sig_type
        self.initial = initial
        self.result = None
        super().__init__(parent, title=("Add Signature" if sig_type == "signature" else "Add Text"))

    def body(self, master):
        master.configure(bg="#f8fafc")
        ttk.Label(master, text=("Signature Text:" if self.sig_type == "signature" else "Text:"),
                 font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=5)
        
        self.entry = ttk.Entry(master, width=40, font=("Segoe UI", 11))
        self.entry.grid(row=0, column=1, padx=10, pady=10)
        if self.initial:
            self.entry.insert(0, self.initial)
        return self.entry

    def apply(self):
        self.result = self.entry.get().strip()

class LivePDFESign:
    def __init__(self, root):
        self.root = root
        self.root.title("Live PDF E-Sign - Professional Document Signing")
        self.root.geometry("1400x900")
        self.root.configure(bg="#0f172a")
        self.root.minsize(1200, 800)

        try:
            self.root.iconbitmap("")
        except:
            pass

        self.pdf_doc = None
        self.pdf_path = None
        self.current_page = 0
        self.signatures = []

        self.dragging_item = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.selected_item = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_dragging = False

        self.colors = {
            'primary': '#3b82f6',
            'primary_hover': '#2563eb',
            'secondary': '#64748b',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'dark': '#1e293b',
            'darker': '#0f172a',
            'light': '#f1f5f9',
            'lighter': '#f8fafc',
            'white': '#ffffff',
            'border': '#e2e8f0',
            'text_primary': '#1e293b',
            'text_secondary': '#64748b',
            'accent': '#8b5cf6'
        }

        self.signature_color = self.colors['primary']
        self.signature_size = 18
        self.text_color = self.colors['text_primary']
        self.text_size = 14

        self.last_drag_time = 0
        self.drag_update_interval = 16

        self.setup_modern_styles()
        self.setup_ui()

    def setup_modern_styles(self):
        style = ttk.Style()
        
        style.configure('Modern.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 10),
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('Modern.TButton',
                 background=[('active', self.colors['primary_hover']),
                           ('pressed', self.colors['primary_hover'])])

        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8),
                       font=('Segoe UI', 9, 'bold'))

        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8),
                       font=('Segoe UI', 9, 'bold'))

        style.configure('Card.TFrame',
                       background=self.colors['white'],
                       relief='flat',
                       borderwidth=1)

        style.configure('Sidebar.TFrame',
                       background=self.colors['lighter'],
                       relief='flat')

        style.configure('Title.TLabel',
                       background=self.colors['lighter'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 14, 'bold'))

        style.configure('Subtitle.TLabel',
                       background=self.colors['lighter'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 10))

        style.configure('Modern.TLabelframe',
                       background=self.colors['white'],
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Modern.TLabelframe.Label',
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 11, 'bold'))

    def setup_ui(self):
        main_container = tk.Frame(self.root, bg=self.colors['lighter'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.create_modern_header(main_container)
        self.create_toolbar(main_container)

        content_frame = tk.Frame(main_container, bg=self.colors['lighter'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        self.create_left_panel(content_frame)
        self.create_pdf_viewer(content_frame)

        self.create_status_bar(main_container)

    def create_modern_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)

        header_content = tk.Frame(header_frame, bg=self.colors['primary'])
        header_content.place(relx=0.5, rely=0.5, anchor='center')

        title_label = tk.Label(header_content, 
                              text="📝 PDF E-Sign Professional",
                              font=('Segoe UI', 20, 'bold'),
                              bg=self.colors['primary'],
                              fg='white')
        title_label.pack(side=tk.LEFT, padx=10)

        subtitle_label = tk.Label(header_content,
                                 text="Drag & Drop • Professional • Secure",
                                 font=('Segoe UI', 11),
                                 bg=self.colors['primary'],
                                 fg='#e2e8f0')
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))

    def create_toolbar(self, parent):
        toolbar_frame = tk.Frame(parent, bg=self.colors['white'], relief='solid', bd=1)
        toolbar_frame.pack(fill=tk.X, pady=(0, 20))

        inner_toolbar = tk.Frame(toolbar_frame, bg=self.colors['white'])
        inner_toolbar.pack(fill=tk.X, padx=20, pady=15)

        file_frame = tk.Frame(inner_toolbar, bg=self.colors['white'])
        file_frame.pack(side=tk.LEFT)

        open_btn = tk.Button(file_frame, 
                           text="📁 Open PDF",
                           command=self.open_pdf,
                           bg=self.colors['primary'],
                           fg='white',
                           font=('Segoe UI', 11, 'bold'),
                           relief='flat',
                           padx=20,
                           pady=10,
                           cursor='hand2',
                           activebackground=self.colors['primary_hover'])
        open_btn.pack(side=tk.LEFT, padx=(0, 10))

        save_btn = tk.Button(file_frame,
                           text="💾 Save As…",
                           command=self.save_pdf,
                           bg=self.colors['success'],
                           fg='white',
                           font=('Segoe UI', 11, 'bold'),
                           relief='flat',
                           padx=20,
                           pady=10,
                           cursor='hand2',
                           activebackground='#059669')
        save_btn.pack(side=tk.LEFT, padx=(0, 10))

        close_btn = tk.Button(file_frame,
                            text="❌ Close",
                            command=self.close_app,
                            bg=self.colors['danger'],
                            fg='white',
                            font=('Segoe UI', 11, 'bold'),
                            relief='flat',
                            padx=20,
                            pady=10,
                            cursor='hand2',
                            activebackground='#dc2626')
        close_btn.pack(side=tk.LEFT)

    def create_left_panel(self, parent):
        self.left_panel = tk.Frame(parent, width=280, bg=self.colors['lighter'])
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        self.left_panel.pack_propagate(False)

        welcome_card = tk.Frame(self.left_panel, bg=self.colors['white'], relief='solid', bd=1)
        welcome_card.pack(fill=tk.X, pady=(0, 10), padx=10)

        welcome_content = tk.Frame(welcome_card, bg=self.colors['white'])
        welcome_content.pack(expand=True, fill=tk.BOTH, padx=30, pady=40)

        icon_label = tk.Label(welcome_content,
                             text="📄",
                             font=('Segoe UI', 48),
                             bg=self.colors['white'],
                             fg=self.colors['primary'])
        icon_label.pack()

        welcome_label = tk.Label(welcome_content,
                                text="Open a PDF document\nto start signing",
                                font=('Segoe UI', 12),
                                bg=self.colors['white'],
                                fg=self.colors['text_secondary'],
                                justify='center')
        welcome_label.pack(pady=(20, 0))

    def create_tools_panel(self):
        for w in self.left_panel.winfo_children():
            w.destroy()

        tools_header = tk.Frame(self.left_panel, bg=self.colors['primary'], height=60)
        tools_header.pack(fill=tk.X, padx=10, pady=(0, 20))
        tools_header.pack_propagate(False)

        title_label = tk.Label(tools_header,
                              text="✒️ Signing Tools",
                              font=('Segoe UI', 14, 'bold'),
                              bg=self.colors['primary'],
                              fg='white')
        title_label.place(relx=0.5, rely=0.5, anchor='center')

        actions_card = tk.Frame(self.left_panel, bg=self.colors['white'], relief='solid', bd=1)
        actions_card.pack(fill=tk.X, padx=10, pady=(0, 20))

        actions_content = tk.Frame(actions_card, bg=self.colors['white'])
        actions_content.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(actions_content, 
                text="Add Content",
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 15))

        signature_btn = tk.Button(actions_content,
                                text="✒️ Add Signature",
                                command=self.add_signature_dialog,
                                bg=self.colors['primary'],
                                fg='white',
                                font=('Segoe UI', 10, 'bold'),
                                relief='flat',
                                cursor='hand2',
                                activebackground=self.colors['primary_hover'])
        signature_btn.pack(fill=tk.X, pady=(0, 10), ipady=8)

        text_btn = tk.Button(actions_content,
                           text="📝 Add Text",
                           command=self.add_text_dialog,
                           bg=self.colors['secondary'],
                           fg='white',
                           font=('Segoe UI', 10, 'bold'),
                           relief='flat',
                           cursor='hand2',
                           activebackground='#475569')
        text_btn.pack(fill=tk.X, pady=(0, 10), ipady=8)

        date_btn = tk.Button(actions_content,
                           text="📅 Add Date",
                           command=self.add_date,
                           bg=self.colors['accent'],
                           fg='white',
                           font=('Segoe UI', 10, 'bold'),
                           relief='flat',
                           cursor='hand2',
                           activebackground='#7c3aed')
        date_btn.pack(fill=tk.X, ipady=8)

        list_card = tk.Frame(self.left_panel, bg=self.colors['white'], relief='solid', bd=1)
        list_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 20))

        list_header = tk.Frame(list_card, bg=self.colors['white'])
        list_header.pack(fill=tk.X, padx=20, pady=(20, 10))

        tk.Label(list_header,
                text="Added Items",
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['text_primary']).pack(anchor='w')

        list_container = tk.Frame(list_card, bg=self.colors['white'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        self.items_listbox = tk.Listbox(list_container,
                                       height=8,
                                       font=('Segoe UI', 10),
                                       bg='#f8fafc',
                                       fg=self.colors['text_primary'],
                                       selectbackground=self.colors['primary'],
                                       selectforeground='white',
                                       relief='solid',
                                       bd=1,
                                       activestyle='none')
        
        scrollbar = tk.Scrollbar(list_container, orient="vertical", bg=self.colors['border'])
        self.items_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.items_listbox.yview)
        
        self.items_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.items_listbox.bind("<Double-1>", self.edit_selected_item)
        self.items_listbox.bind("<<ListboxSelect>>", self.highlight_selected_item)

        btn_frame = tk.Frame(list_card, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        edit_btn = tk.Button(btn_frame,
                           text="✏️ Edit",
                           command=self.edit_selected_item,
                           bg=self.colors['warning'],
                           fg='white',
                           font=('Segoe UI', 9, 'bold'),
                           relief='flat',
                           cursor='hand2',
                           activebackground='#d97706')
        edit_btn.pack(side=tk.LEFT, padx=(0, 10), ipady=5, ipadx=10)

        delete_btn = tk.Button(btn_frame,
                             text="🗑️ Delete",
                             command=self.delete_selected_item,
                             bg=self.colors['danger'],
                             fg='white',
                             font=('Segoe UI', 9, 'bold'),
                             relief='flat',
                             cursor='hand2',
                             activebackground='#dc2626')
        delete_btn.pack(side=tk.LEFT, ipady=5, ipadx=10)

        tips_card = tk.Frame(self.left_panel, bg='#e0f2fe', relief='solid', bd=1)
        tips_card.pack(fill=tk.X, padx=10)

        tips_content = tk.Frame(tips_card, bg='#e0f2fe')
        tips_content.pack(fill=tk.X, padx=15, pady=15)

        tip_icon = tk.Label(tips_content,
                           text="💡",
                           font=('Segoe UI', 16),
                           bg='#e0f2fe')
        tip_icon.pack()

        tip_text = tk.Label(tips_content,
                           text="Drag & Drop Magic!\nClick and drag signatures\nto reposition them perfectly",
                           font=('Segoe UI', 9, 'italic'),
                           bg='#e0f2fe',
                           fg='#0369a1',
                           justify='center')
        tip_text.pack(pady=(5, 0))

    def create_pdf_viewer(self, parent):
        viewer_container = tk.Frame(parent, bg=self.colors['lighter'])
        viewer_container.pack(fill=tk.BOTH, expand=True)

        shadow_frame = tk.Frame(viewer_container, bg='#cbd5e1', height=600)
        shadow_frame.pack(fill=tk.BOTH, expand=True, padx=(3, 0), pady=(3, 0))

        canvas_frame = tk.Frame(shadow_frame, bg=self.colors['white'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 3), pady=(0, 3))

        self.canvas = tk.Canvas(canvas_frame, 
                               bg=self.colors['white'], 
                               cursor="arrow", 
                               highlightthickness=0, 
                               relief="flat")
        
        v_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)

        self.show_welcome_message()

    def create_status_bar(self, parent):
        status_container = tk.Frame(parent, bg=self.colors['dark'], height=40)
        status_container.pack(fill=tk.X, pady=(20, 0))
        status_container.pack_propagate(False)

        status_content = tk.Frame(status_container, bg=self.colors['dark'])
        status_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.status_var = tk.StringVar(value="📄 Ready to sign documents professionally")
        status_label = tk.Label(status_content,
                               textvariable=self.status_var,
                               font=('Segoe UI', 10),
                               bg=self.colors['dark'],
                               fg='white',
                               anchor='w')
        status_label.pack(fill=tk.X)

    def show_welcome_message(self):
        self.canvas.delete("all")
    
        canvas_width = self.canvas.winfo_reqwidth() or 800
        canvas_height = self.canvas.winfo_reqheight() or 600
        
        # Draw a subtle grid background
        for i in range(0, canvas_width, 50):
            for j in range(0, canvas_height, 50):
                self.canvas.create_rectangle(i, j, i+25, j+25, fill='#f8fafc', outline='#f1f5f9', width=1)

        center_x = canvas_width // 2
        center_y = canvas_height // 2

        # Draw the target icon (🎯 replaced with a styled text representation)
        self.canvas.create_text(center_x, center_y - 100,
                            text="🎯",
                            font=('Segoe UI', 72),
                            fill=self.colors['primary'],
                            anchor="center")

        # Main welcome title
        self.canvas.create_text(center_x, center_y - 20,
                            text="Welcome to PDF E-Sign Professional",
                            font=('Segoe UI', 20, 'bold'),
                            fill=self.colors['text_primary'],
                            anchor="nw")

        # Features list
        features = [
            "📁 Open any PDF document",
            "✒️ Add professional signatures",
            "🖱️ Smooth drag & drop positioning",
            "💾 Save with embedded content",
            "🎨 Modern, intuitive interface"
        ]

        y_offset = 40
        for feature in features:
            self.canvas.create_text(center_x, center_y + y_offset,
                                text=feature,
                                font=('Segoe UI', 12),
                                fill=self.colors['text_secondary'],
                                anchor="center")
            y_offset += 30

        # Call to action
        self.canvas.create_text(center_x, center_y + y_offset + 30,
                            text="Click 'Open PDF' to get started! 🚀",
                            font=('Segoe UI', 14, 'bold'),
                            fill=self.colors['primary'],
                            anchor="center")

    def open_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF Document", 
            filetypes=[("PDF files", "*.pdf")]
        )
        if not file_path:
            return
        try:
            if self.pdf_doc:
                self.pdf_doc.close()
            self.pdf_doc = fitz.open(file_path)
            self.pdf_path = file_path
            self.current_page = 0
            self.signatures = []
            self.selected_item = None
            self.dragging_item = None

            self.create_tools_panel()
            self.display_page()

            filename = os.path.basename(file_path)
            self.status_var.set(f"📄 Loaded: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF:\n{e}")

    def close_app(self):
        if self.pdf_doc:
            self.pdf_doc.close()
        self.root.destroy()

    def display_page(self):
        if not self.pdf_doc:
            self.show_welcome_message()
            return
        try:
            page = self.pdf_doc[self.current_page]
            zoom_level = 1.0
            mat = fitz.Matrix(zoom_level, zoom_level)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")

            pil_image = Image.open(io.BytesIO(img_data))
            self.photo = ImageTk.PhotoImage(pil_image)

            self.canvas.delete("all")
            self.canvas.create_image(25, 25, anchor="nw", image=self.photo, tags="pdf_page")

            bbox = self.canvas.bbox("pdf_page")
            if bbox:
                self.canvas.create_rectangle(bbox[0]-1, bbox[1]-1, bbox[2]+1, bbox[3]+1, 
                                           outline='#cbd5e1', width=2, tags="pdf_shadow")
                self.canvas.create_rectangle(bbox[0]-3, bbox[1]-3, bbox[2]+1, bbox[3]+1, 
                                           outline='#e2e8f0', width=1, tags="pdf_border")

            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.redraw_signatures()
            self.update_items_listbox()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to display page:\n{e}")

    def redraw_signatures(self):
        for i, sig in enumerate(self.signatures):
            if sig["page"] == self.current_page:
                self.draw_signature_on_canvas(sig, i)

    def draw_signature_on_canvas(self, sig, index):
        zoom_level = 1.0
        x = 25 + (sig["x"] * zoom_level)
        y = 25 + (sig["y"] * zoom_level)
        size = int(sig["size"] * zoom_level)

        if sig["type"] == "signature":
            font_style = ("Times", size, "italic")  
        elif sig["type"] == "date":
            font_style = ("Segoe UI", size, "bold")
        else:
            font_style = ("Segoe UI", size)

        text_id = self.canvas.create_text(x, y, text=sig["text"], anchor="nw", font=font_style, fill=sig["color"], tags=f"sig_{index}")
        bbox = self.canvas.bbox(f"sig_{index}")
        
        if bbox:
            self.canvas.delete(f"sig_{index}")
            
            shadow_offset = 2
            self.canvas.create_text(x+shadow_offset, y+shadow_offset, text=sig["text"], anchor="nw", 
                                   font=font_style, fill="#e2e8f0", tags=f"sig_shadow2_{index}")
            self.canvas.create_text(x+1, y+1, text=sig["text"], anchor="nw", 
                                   font=font_style, fill="#cbd5e1", tags=f"sig_shadow_{index}")
            
            padding = 6
            bg_id = self.canvas.create_rectangle(bbox[0]-padding, bbox[1]-padding, 
                                               bbox[2]+padding, bbox[3]+padding, 
                                               fill="white", outline="#e2e8f0", width=1, 
                                               tags=f"sig_bg_{index}")
            
            text_id = self.canvas.create_text(x, y, text=sig["text"], anchor="nw", 
                                            font=font_style, fill=sig["color"], tags=f"sig_{index}")
            
            self.canvas.tag_lower(f"sig_shadow2_{index}", f"sig_shadow_{index}")
            self.canvas.tag_lower(f"sig_shadow_{index}", f"sig_bg_{index}")
            self.canvas.tag_lower(f"sig_bg_{index}", f"sig_{index}")

        if self.selected_item == index:
            bbox = self.canvas.bbox(f"sig_{index}")
            if bbox:
                glow_padding = 8
                self.canvas.create_rectangle(bbox[0]-glow_padding, bbox[1]-glow_padding, 
                                           bbox[2]+glow_padding, bbox[3]+glow_padding, 
                                           outline=self.colors['primary'], width=3, 
                                           dash=(10, 5), tags=f"selection_glow_{index}")
                
                self.canvas.create_rectangle(bbox[0]-6, bbox[1]-4, bbox[2]+6, bbox[3]+4, 
                                           outline=self.colors['primary'], width=2, 
                                           tags=f"selection_{index}")
                
                corner_size = 5
                corners = [(bbox[0]-6, bbox[1]-4), (bbox[2]+6, bbox[1]-4), 
                          (bbox[0]-6, bbox[3]+4), (bbox[2]+6, bbox[3]+4)]
                for i, (cx, cy) in enumerate(corners):
                    self.canvas.create_oval(cx-corner_size, cy-corner_size, 
                                          cx+corner_size, cy+corner_size, 
                                          fill=self.colors['primary'], outline='white', 
                                          width=2, tags=f"corner_{index}_{i}")

        sig["canvas_x"] = x
        sig["canvas_y"] = y
        sig["canvas_id"] = text_id

    def on_canvas_click(self, event):
        if not self.pdf_doc:
            return
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        clicked_item = self.get_signature_at_position(canvas_x, canvas_y)
        if clicked_item is not None:
            self.dragging_item = clicked_item
            self.selected_item = clicked_item
            self.is_dragging = True
            sig = self.signatures[clicked_item]
            self.drag_start_x = canvas_x
            self.drag_start_y = canvas_y
            self.drag_offset_x = canvas_x - sig["canvas_x"]
            self.drag_offset_y = canvas_y - sig["canvas_y"]
            self.canvas.configure(cursor="hand2")
            self.status_var.set(f"🖱️ Dragging: {sig['text'][:25]}... (release to drop)")
        else:
            self.selected_item = None
            self.is_dragging = False
        self.display_page()

    def on_canvas_drag(self, event):
        if not self.is_dragging or self.dragging_item is None:
            return
        current_time = time.time() * 1000
        if current_time - self.last_drag_time < self.drag_update_interval:
            return
        self.last_drag_time = current_time

        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        sig = self.signatures[self.dragging_item]
        new_canvas_x = canvas_x - self.drag_offset_x
        new_canvas_y = canvas_y - self.drag_offset_y

        zoom_level = 1.0
        new_x = max(0, (new_canvas_x - 25) / zoom_level)
        new_y = max(0, (new_canvas_y - 25) / zoom_level)

        if self.pdf_doc:
            page = self.pdf_doc[self.current_page]
            max_x = page.rect.width - 100
            max_y = page.rect.height - 50
            new_x = min(new_x, max_x)
            new_y = min(new_y, max_y)

        sig["x"] = new_x
        sig["y"] = new_y
        self.move_signature_on_canvas(self.dragging_item, new_canvas_x, new_canvas_y)
        self.status_var.set(f"🖱️ Dragging: {sig['text'][:25]} to ({int(new_x)}, {int(new_y)})")

    def move_signature_on_canvas(self, index, new_x, new_y):
        sig = self.signatures[index]
        if "canvas_id" in sig:
            old_x = sig["canvas_x"]
            old_y = sig["canvas_y"]
            dx = new_x - old_x
            dy = new_y - old_y
            self.canvas.move(f"sig_{index}", dx, dy)
            self.canvas.move(f"sig_bg_{index}", dx, dy)
            self.canvas.move(f"sig_shadow_{index}", dx, dy)
            self.canvas.move(f"sig_shadow2_{index}", dx, dy)
            self.canvas.move(f"selection_{index}", dx, dy)
            self.canvas.move(f"selection_glow_{index}", dx, dy)
            for i in range(4):
                self.canvas.move(f"corner_{index}_{i}", dx, dy)
            sig["canvas_x"] = new_x
            sig["canvas_y"] = new_y

    def on_canvas_release(self, event):
        if self.dragging_item is not None:
            sig = self.signatures[self.dragging_item]
            grid_size = 5
            sig["x"] = round(sig["x"] / grid_size) * grid_size
            sig["y"] = round(sig["y"] / grid_size) * grid_size
            self.display_page()
            self.status_var.set(f"📍 Positioned: {sig['text'][:25]} at ({int(sig['x'])}, {int(sig['y'])})")
        self.is_dragging = False
        self.dragging_item = None
        self.canvas.configure(cursor="arrow")
        self.last_drag_time = 0

    def on_canvas_double_click(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        clicked_item = self.get_signature_at_position(canvas_x, canvas_y)
        if clicked_item is not None:
            self.edit_signature(clicked_item)

    def on_mouse_motion(self, event):
        if not self.pdf_doc or self.is_dragging:
            return
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        hover_item = self.get_signature_at_position(canvas_x, canvas_y)
        if hover_item is not None:
            self.canvas.configure(cursor="hand2")
            sig = self.signatures[hover_item]
            self.status_var.set(f"🖱️ Hover: {sig['text'][:30]} (click to select, double-click to edit)")
        else:
            self.canvas.configure(cursor="arrow")
            if not self.is_dragging:
                self.status_var.set("📄 Document ready - Click 'Add Signature' to start signing")

    def get_signature_at_position(self, canvas_x, canvas_y):
        for i, sig in enumerate(self.signatures):
            if sig["page"] == self.current_page and "canvas_x" in sig:
                bbox = self.canvas.bbox(f"sig_{i}")
                if bbox:
                    padding = 5
                    if (bbox[0] - padding <= canvas_x <= bbox[2] + padding and bbox[1] - padding <= canvas_y <= bbox[3] + padding):
                        return i
        return None

    def add_signature_dialog(self):
        dialog = SignatureDialog(self.root, "signature")
        if dialog.result:
            self.add_signature_at_center(dialog.result, "signature")

    def add_text_dialog(self):
        dialog = SignatureDialog(self.root, "text")
        if dialog.result:
            self.add_signature_at_center(dialog.result, "text")

    def add_date(self):
        date_str = datetime.now().strftime("%B %d, %Y")
        self.add_signature_at_center(date_str, "date")

    def add_signature_at_center(self, text, sig_type):
        if not self.pdf_doc:
            return
        page = self.pdf_doc[self.current_page]
        page_width, page_height = page.rect.width, page.rect.height
        
        size = self.signature_size if sig_type == "signature" else self.text_size
        color = self.signature_color if sig_type == "signature" else self.text_color
        
        sig = {
            "text": text,
            "type": sig_type,
            "x": (page_width - 100) / 2,
            "y": (page_height - 30) / 2,
            "size": size,
            "color": color,
            "page": self.current_page,
        }
        self.signatures.append(sig)
        self.display_page()
        self.status_var.set(f"➕ Added: {text[:25]}")

    def update_items_listbox(self):
        if hasattr(self, "items_listbox"):
            self.items_listbox.delete(0, tk.END)
            for i, sig in enumerate(self.signatures):
                if sig["page"] == self.current_page:
                    display_text = f"{sig['type'].title()}: {sig['text'][:25]}"
                    self.items_listbox.insert(tk.END, display_text)

    def highlight_selected_item(self, event=None):
        if hasattr(self, "items_listbox"):
            sel = self.items_listbox.curselection()
            if sel:
                index = sel[0]
                sigs_on_page = [i for i, s in enumerate(self.signatures) if s["page"] == self.current_page]
                if index < len(sigs_on_page):
                    self.selected_item = sigs_on_page[index]
                    self.display_page()

    def edit_selected_item(self, event=None):
        sel = self.items_listbox.curselection() if hasattr(self, "items_listbox") else []
        if sel:
            index = sel[0]
            sigs_on_page = [i for i, s in enumerate(self.signatures) if s["page"] == self.current_page]
            if index < len(sigs_on_page):
                self.edit_signature(sigs_on_page[index])

    def edit_signature(self, index):
        sig = self.signatures[index]
        dialog = SignatureDialog(self.root, sig["type"], initial=sig["text"])
        if dialog.result:
            self.signatures[index]["text"] = dialog.result
            self.display_page()
            self.status_var.set(f"✏️ Edited: {dialog.result[:25]}")

    def delete_selected_item(self):
        sel = self.items_listbox.curselection() if hasattr(self, "items_listbox") else []
        if sel:
            index = sel[0]
            sigs_on_page = [i for i, s in enumerate(self.signatures) if s["page"] == self.current_page]
            if index < len(sigs_on_page):
                actual_index = sigs_on_page[index]
                removed = self.signatures.pop(actual_index)
                self.display_page()
                self.status_var.set(f"🗑️ Deleted: {removed['text'][:25]}")

    def hex_to_rgb01(self, color_str):
        if not color_str:
            return (0, 0, 0)
        s = color_str.strip()
        if s.startswith("#"):
            s = s[1:]
        if len(s) == 3:
            s = "".join([c * 2 for c in s])
        try:
            r = int(s[0:2], 16) / 255.0
            g = int(s[2:4], 16) / 255.0
            b = int(s[4:6], 16) / 255.0
            return (r, g, b)
        except Exception:
            return (0, 0, 0)

    def save_pdf(self):
        if not self.pdf_doc:
            messagebox.showwarning("Warning", "Please open a PDF document first.")
            return
        
        initial = os.path.splitext(os.path.basename(self.pdf_path or "signed.pdf"))[0] + "_signed.pdf"
        out_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF", "*.pdf")], 
            initialfile=initial, 
            title="Save Signed PDF"
        )
        if not out_path:
            return
        
        try:
            doc = fitz.open(self.pdf_path) if self.pdf_path else self.pdf_doc
            
            for i, sig in enumerate(self.signatures):
                page = doc[sig["page"]]
                fontsize = float(sig["size"])
                color = self.hex_to_rgb01(sig["color"])
                fontname = "Times-Italic" if sig["type"] == "signature" else ("Helvetica-Bold" if sig["type"] == "date" else "Helvetica")
                
                x = max(0, min(sig["x"], page.rect.width - 2))
                y = max(0, min(sig["y"], page.rect.height - 2))
                
                page.insert_text(
                    fitz.Point(x, y),
                    sig["text"],
                    fontsize=fontsize,
                    fontname=fontname,
                    fill=color, 
                )
            
            if doc is self.pdf_doc:
                doc.save(out_path)
            else:
                doc.save(out_path)
                doc.close()
            
            self.status_var.set(f"✅ Successfully saved: {os.path.basename(out_path)}")
            
            success_msg = f"Your signed PDF has been saved successfully!\n\n📁 Location: {out_path}\n\n🎉 Ready to share or print!"
            messagebox.showinfo("Success - Document Saved", success_msg)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF:\n{str(e)}\n\nPlease check file permissions and try again.")

if __name__ == "__main__":
    root = tk.Tk()
    
    try:
        style = ttk.Style()
        available_themes = style.theme_names()
        if "clam" in available_themes:
            style.theme_use("clam")
        elif "vista" in available_themes:
            style.theme_use("vista")
        elif "xpnative" in available_themes:
            style.theme_use("xpnative")
    except Exception:
        pass
    
    app = LivePDFESign(root)
    
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()