import math
import tkinter as tk
from tkinter import messagebox, simpledialog
from models import Edge, Vertex
from utils import calculate_distance, point_to_segment_distance


class GraphEditor:

  def __init__(self, root):
    self.root = root
    self.root.title("Editor Visual de Grafos")
    self.root.geometry("950x650")

    # Estruturas de Dados
    self.vertices = []
    self.edges = []
    self.vertex_counter = 1

    # Estado da Aplicação
    self.mode = tk.StringVar(value="add_vertex")
    self.selected_vertex_for_edge = None

    self._setup_ui()

  def _setup_ui(self):
    # 1. Barra de Ferramentas Superior
    self.toolbar = tk.Frame(self.root, bg="#f0f0f0", bd=2, relief=tk.RAISED)
    self.toolbar.pack(side=tk.TOP, fill=tk.X)

    tk.Label(
        self.toolbar, text="Modo:", bg="#f0f0f0", font=("Arial", 10, "bold")
    ).pack(side=tk.LEFT, padx=8, pady=5)

    modes = [
        ("Mover", "select"),
        ("Adicionar Vértice", "add_vertex"),
        ("Adicionar Aresta", "add_edge"),
        ("Remover", "remove"),
    ]

    for text, mode_value in modes:
      rb = tk.Radiobutton(
          self.toolbar,
          text=text,
          value=mode_value,
          variable=self.mode,
          indicatoron=0,
          padx=10,
          pady=5,
          bg="#ffffff",
          selectcolor="#d0e0ff",
          command=self._on_mode_change,
      )
      rb.pack(side=tk.LEFT, padx=3, pady=5)

    # Botões Extras na Barra de Ferramentas
    btn_matrix = tk.Button(
        self.toolbar,
        text="Matriz de Adjacência",
        command=self.show_adjacency_matrix,
        bg="#e1f5fe",
    )
    btn_matrix.pack(side=tk.RIGHT, padx=5, pady=5)

    btn_clear = tk.Button(
        self.toolbar,
        text="Limpar Tudo",
        command=self.clear_all,
        bg="#ffebee",
    )
    btn_clear.pack(side=tk.RIGHT, padx=5, pady=5)

    # 2. Tela de Desenho (Canvas)
    self.canvas = tk.Canvas(self.root, bg="white")
    self.canvas.pack(fill=tk.BOTH, expand=True)

    # Eventos do Mouse
    self.canvas.bind("<Button-1>", self.on_canvas_click)
    self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)

    # 3. Barra de Status Inferior
    self.status_var = tk.StringVar(
        value="Modo Adicionar Vértice: Clique em um local livre do canvas para criar um nó."
    )
    status_bar = tk.Label(
        self.root,
        textvariable=self.status_var,
        bd=1,
        relief=tk.SUNKEN,
        anchor=tk.W,
        bg="#fafafa",
    )
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

  def _on_mode_change(self):
    """Atualiza o texto da barra de status e limpa seleções pendentes ao trocar de modo."""
    self.selected_vertex_for_edge = None
    self.redraw_canvas()

    m = self.mode.get()
    if m == "add_vertex":
      self.status_var.set(
          "Modo Adicionar Vértice: Clique em um local livre do canvas."
      )
    elif m == "select":
      self.status_var.set(
          "Modo Mover: Clique e arraste um vértice. Duplo clique para editar."
      )
    elif m == "add_edge":
      self.status_var.set(
          "Modo Adicionar Aresta: Clique no vértice de ORIGEM."
      )
    elif m == "remove":
      self.status_var.set(
          "Modo Remover: Clique sobre um vértice ou aresta para excluí-lo."
      )

  def get_vertex_at(self, x, y):
    """Verifica se o clique (x, y) ocorreu dentro de algum vértice existente."""
    for v in reversed(self.vertices):
      if calculate_distance(x, y, v.x, v.y) <= v.radius:
        return v
    return None

  def get_edge_at(self, x, y):
    """Verifica se o clique (x, y) ocorreu próximo a alguma aresta existente."""
    for edge in reversed(self.edges):
      if edge.source == edge.target:
        # Verifica laço (self-loop)
        v = edge.source
        if calculate_distance(x, y, v.x, v.y - v.radius - 15) <= 15:
          return edge
      else:
        dist = point_to_segment_distance(
            x,
            y,
            edge.source.x,
            edge.source.y,
            edge.target.x,
            edge.target.y,
        )
        if dist <= 8:  # Tolerância de 8 pixels ao redor da linha
          return edge
    return None

  def on_canvas_click(self, event):
    """Gerencia o evento de clique simples com base no modo ativo."""
    x, y = event.x, event.y
    current_mode = self.mode.get()

    # --- MODO: ADICIONAR VÉRTICE ---
    if current_mode == "add_vertex":
      if not self.get_vertex_at(x, y):
        default_name = f"V{self.vertex_counter}"
        name = simpledialog.askstring(
            "Novo Vértice",
            "Nome do Vértice:",
            initialvalue=default_name,
            parent=self.root,
        )

        if name is not None and name.strip() != "":
          new_vertex = Vertex(self.vertex_counter, name.strip(), x, y)
          self.vertices.append(new_vertex)
          self.vertex_counter += 1
          self.redraw_canvas()

    # --- MODO: ADICIONAR ARESTA ---
    elif current_mode == "add_edge":
      clicked_vertex = self.get_vertex_at(x, y)

      if clicked_vertex:
        if self.selected_vertex_for_edge is None:
          self.selected_vertex_for_edge = clicked_vertex
          self.status_var.set(
              f"Origem selecionada: '{clicked_vertex.label}'. Agora clique no vértice de DESTINO."
          )
          self.redraw_canvas()
        else:
          source_v = self.selected_vertex_for_edge
          target_v = clicked_vertex

          weight = simpledialog.askstring(
              "Nova Aresta",
              "Peso/Rótulo da aresta:",
              initialvalue="1",
              parent=self.root,
          )

          if weight is not None:
            is_directed = messagebox.askyesno(
                "Direção da Aresta",
                "A aresta é direcionada (com seta)?",
                parent=self.root,
            )
            new_edge = Edge(
                source_v, target_v, weight=weight, directed=is_directed
            )
            self.edges.append(new_edge)

          self.selected_vertex_for_edge = None
          self.status_var.set(
              "Aresta criada! Clique no próximo vértice de origem."
          )
          self.redraw_canvas()
      else:
        self.selected_vertex_for_edge = None
        self.status_var.set(
            "Seleção cancelada. Clique no vértice de ORIGEM."
        )
        self.redraw_canvas()

    # --- MODO: REMOVER ELEMENTO ---
    elif current_mode == "remove":
      clicked_vertex = self.get_vertex_at(x, y)
      if clicked_vertex:
        self.remove_vertex(clicked_vertex)
        return

      clicked_edge = self.get_edge_at(x, y)
      if clicked_edge:
        self.remove_edge(clicked_edge)
        return

  def on_canvas_double_click(self, event):
    """Trata o duplo clique no canvas para alterar rótulos ou pesos."""
    x, y = event.x, event.y

    # 1. Tenta alterar Vértice
    clicked_vertex = self.get_vertex_at(x, y)
    if clicked_vertex:
      new_name = simpledialog.askstring(
          "Alterar Vértice",
          "Novo nome/rótulo:",
          initialvalue=clicked_vertex.label,
          parent=self.root,
      )
      if new_name is not None and new_name.strip() != "":
        clicked_vertex.label = new_name.strip()
        self.redraw_canvas()
      return

    # 2. Tenta alterar Aresta
    clicked_edge = self.get_edge_at(x, y)
    if clicked_edge:
      new_weight = simpledialog.askstring(
          "Alterar Aresta",
          "Novo peso/rótulo:",
          initialvalue=clicked_edge.weight,
          parent=self.root,
      )
      if new_weight is not None:
        is_directed = messagebox.askyesno(
            "Direção da Aresta",
            "A aresta é direcionada?",
            parent=self.root,
        )
        clicked_edge.weight = new_weight
        clicked_edge.directed = is_directed
        self.redraw_canvas()

  def remove_vertex(self, vertex):
    """Remove um vértice e limpa todas as arestas ligadas a ele."""
    self.vertices.remove(vertex)
    self.edges = [
        e for e in self.edges if e.source != vertex and e.target != vertex
    ]
    if self.selected_vertex_for_edge == vertex:
      self.selected_vertex_for_edge = None
    self.redraw_canvas()

  def remove_edge(self, edge):
    """Remove uma aresta específica."""
    self.edges.remove(edge)
    self.redraw_canvas()

  def clear_all(self):
    """Limpa todo o grafo do canvas."""
    if messagebox.askyesno(
        "Limpar Tudo",
        "Deseja remover todos os vértices e arestas?",
        parent=self.root,
    ):
      self.vertices.clear()
      self.edges.clear()
      self.vertex_counter = 1
      self.selected_vertex_for_edge = None
      self.redraw_canvas()

  def redraw_canvas(self):
    """Limpa o canvas e redesenha todas as arestas e vértices."""
    self.canvas.delete("all")

    for e in self.edges:
      self.draw_edge(e)

    for v in self.vertices:
      is_selected = v == self.selected_vertex_for_edge
      fill_color = "#ff8a80" if is_selected else "#82b1ff"
      outline_color = "#d50000" if is_selected else "#2979ff"

      self.canvas.create_oval(
          v.x - v.radius,
          v.y - v.radius,
          v.x + v.radius,
          v.y + v.radius,
          fill=fill_color,
          outline=outline_color,
          width=2,
      )

      self.canvas.create_text(
          v.x,
          v.y,
          text=v.label,
          font=("Arial", 10, "bold"),
          fill="#ffffff" if is_selected else "#000000",
      )

  def draw_edge(self, edge):
    """Calcula as posições e desenha uma única aresta no canvas."""
    src, tgt = edge.source, edge.target

    if src == tgt:
      r = src.radius
      self.canvas.create_oval(
          src.x - r,
          src.y - 2 * r - 10,
          src.x + r,
          src.y,
          outline="#37474f",
          width=2,
      )
      self.canvas.create_text(
          src.x,
          src.y - 2 * r - 18,
          text=edge.weight,
          font=("Arial", 9, "bold"),
          fill="#c62828",
      )
      return

    angle = math.atan2(tgt.y - src.y, tgt.x - src.x)
    x1 = src.x + src.radius * math.cos(angle)
    y1 = src.y + src.radius * math.sin(angle)
    x2 = tgt.x - tgt.radius * math.cos(angle)
    y2 = tgt.y - tgt.radius * math.sin(angle)

    arrow_opt = tk.LAST if edge.directed else None

    self.canvas.create_line(
        x1,
        y1,
        x2,
        y2,
        fill="#37474f",
        width=2,
        arrow=arrow_opt,
        arrowshape=(10, 12, 5),
    )

    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    perp_x = -math.sin(angle) * 12
    perp_y = math.cos(angle) * 12

    self.canvas.create_text(
        mid_x + perp_x,
        mid_y + perp_y,
        text=edge.weight,
        font=("Arial", 9, "bold"),
        fill="#c62828",
    )

  def show_adjacency_matrix(self):
      """Gera e exibe a Matriz de Adjacência em uma nova janela."""
      if not self.vertices:
        messagebox.showinfo("Matriz de Adjacência", "O grafo está vazio!")
        return

      n = len(self.vertices)
      matrix = [[0] * n for _ in range(n)]

      # Preenche a matriz buscando pelo objeto exato do vértice
      for edge in self.edges:
        try:
          i = self.vertices.index(edge.source)
          j = self.vertices.index(edge.target)

          try:
            val = float(edge.weight)
            weight_val = int(val) if val.is_integer() else val
          except ValueError:
            weight_val = 1

          matrix[i][j] += weight_val

          if not edge.directed and i != j:
            matrix[j][i] += weight_val

        except ValueError:
          continue

      # Formatação dos cabeçalhos e colunas
      labels = [v.label for v in self.vertices]
      header = "    " + "  ".join(f"{lbl:>6}" for lbl in labels)
      lines = [header, "-" * len(header)]

      for idx, row in enumerate(matrix):
        row_str = (
            f"{labels[idx]:>3} |" + "  ".join(f"{val:>6}" for val in row)
        )
        lines.append(row_str)

      matrix_text = "\n".join(lines)

      # Criar janela pop-up
      win = tk.Toplevel(self.root)
      win.title("Matriz de Adjacência")
      win.geometry("500x350")

      # Componente Text com cores de fundo (bg) e texto (fg) explicitamente definidas
      text_widget = tk.Text(
          win,
          font=("Courier", 10, "bold"),
          bg="#ffffff",  # Fundo branco forçado
          fg="#000000",  # Texto preto forçado
          padx=10,
          pady=10,
      )
      text_widget.insert(tk.END, matrix_text)

      # Torna o texto apenas para leitura
      text_widget.config(state=tk.DISABLED)
      text_widget.pack(fill=tk.BOTH, expand=True)

      # Garante que a janela sobressaia na tela
      win.lift()
      win.focus_force()