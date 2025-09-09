import tkinter as tk
import threading
import time
from simulation.simulation import Simulation
from utils.config import r, d, e, n, u, MAX_TICKS
from utils.config import CANVAS_WIDTH, CANVAS_HEIGHT, ROAD_WIDTH, CAR_SIZE, IN_LENGTH
from simulation.static_simulation import StaticSimulation  # Asegúrate de tener este import
import tkinter.messagebox as messagebox

class TrafficSimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚦 Simulador de Semáforos Auto-Organizantes")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')

        # Variable para tipo de simulación
        self.sim_type = tk.StringVar(value="auto")  # "auto" o "static"

        # Variables de simulación
        self.simulation = None
        self.running = False
        self.paused = False
        self.tick_count = 0

        # Crear la interfaz
        self.create_widgets()

        # Inicializar simulación
        self.reset_simulation()

    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame superior para controles
        control_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Título
        title_label = tk.Label(control_frame, text="🚦 SIMULADOR DE SEMÁFOROS AUTO-ORGANIZANTES",
                              font=('Arial', 16, 'bold'), bg='#34495e', fg='white')
        title_label.pack(pady=10)

        sim_type_frame = tk.Frame(control_frame, bg='#34495e')
        sim_type_frame.pack(pady=5)
        tk.Label(sim_type_frame, text="Tipo de simulación:", bg='#34495e', fg='white', font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        tk.Radiobutton(sim_type_frame, text="Autoorganizada", variable=self.sim_type, value="auto",
                       bg='#34495e', fg='white', selectcolor='#2ecc71', font=('Arial', 10)).pack(side=tk.LEFT)
        tk.Radiobutton(sim_type_frame, text="Estática", variable=self.sim_type, value="static",
                       bg='#34495e', fg='white', selectcolor='#e67e22', font=('Arial', 10)).pack(side=tk.LEFT)
        
        # Botones de control
        button_frame = tk.Frame(control_frame, bg='#34495e')
        button_frame.pack(pady=5)

        self.compare_btn = tk.Button(button_frame, text="📊 Comparar 10x10", command=self.run_batch_comparison,
                                    bg='#2980b9', fg='white', font=('Arial', 12, 'bold'))
        self.compare_btn.pack(side=tk.LEFT, padx=5)

        self.start_btn = tk.Button(button_frame, text="▶️ Iniciar", command=self.start_simulation,
                                  bg='#27ae60', fg='white', font=('Arial', 12, 'bold'))
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = tk.Button(button_frame, text="⏸️ Pausar", command=self.pause_simulation,
                                  bg='#f39c12', fg='white', font=('Arial', 12, 'bold'))
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = tk.Button(button_frame, text="🔄 Reiniciar", command=self.reset_simulation,
                                  bg='#e74c3c', fg='white', font=('Arial', 12, 'bold'))
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # Control de velocidad
        speed_frame = tk.Frame(control_frame, bg='#34495e')
        speed_frame.pack(pady=5)

        tk.Label(speed_frame, text="Velocidad:", bg='#34495e', fg='white', font=('Arial', 10)).pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=0.8)
        speed_scale = tk.Scale(speed_frame, from_=0.1, to=2.0, resolution=0.1,
                              variable=self.speed_var, orient=tk.HORIZONTAL,
                              bg='#34495e', fg='white', highlightthickness=0)
        speed_scale.pack(side=tk.LEFT, padx=5)

        # Frame para canvas y estadísticas
        content_frame = tk.Frame(main_frame, bg='#2c3e50')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas para la simulación
        canvas_frame = tk.Frame(content_frame, bg='#2c3e50')
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                               bg='#1a252f', highlightthickness=2, highlightbackground='#34495e')
        self.canvas.pack(padx=5, pady=5)

        # Frame derecho para estadísticas
        stats_frame = tk.Frame(content_frame, bg='#34495e', width=200, relief=tk.RAISED, bd=2)
        stats_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0), pady=5)
        stats_frame.pack_propagate(False)

        # Estadísticas en tiempo real
        tk.Label(stats_frame, text="📊 ESTADÍSTICAS", font=('Arial', 14, 'bold'),
                bg='#34495e', fg='white').pack(pady=10)

        self.stats_labels = {}
        stats_info = [
            ("tick", "⏰ Tick:"),
            ("lightA", "🚦 Semáforo A:"),
            ("lightB", "🚦 Semáforo B:"),
            ("carsA", "🚗 Cola A:"),
            ("carsB", "🚗 Cola B:"),
            ("crossedA", "✅ Cruzaron A:"),
            ("crossedB", "✅ Cruzaron B:"),
            ("totalCrossed", "🏁 Total:"),
            ("efficiency", "📈 Eficiencia:")
        ]

        for key, label in stats_info:
            frame = tk.Frame(stats_frame, bg='#34495e')
            frame.pack(fill=tk.X, padx=10, pady=2)

            tk.Label(frame, text=label, bg='#34495e', fg='#bdc3c7',
                    font=('Arial', 10), anchor='w').pack(side=tk.LEFT)

            self.stats_labels[key] = tk.Label(frame, text="0", bg='#34495e', fg='white',
                                             font=('Arial', 10, 'bold'), anchor='e')
            self.stats_labels[key].pack(side=tk.RIGHT)

        # Leyenda
        legend_frame = tk.LabelFrame(stats_frame, text="🎯 Leyenda", bg='#34495e', fg='white',
                                    font=('Arial', 12, 'bold'))
        legend_frame.pack(fill=tk.X, padx=10, pady=20)

        legend_items = [
            ("🟦", "Carros normales"),
            ("🟥", "Zona crítica"),
            ("🟨", "Zona de salida"),
            ("🔴", "Semáforo rojo"),
            ("🟡", "Semáforo amarillo"),
            ("🟢", "Semáforo verde")
        ]

        for symbol, desc in legend_items:
            frame = tk.Frame(legend_frame, bg='#34495e')
            frame.pack(fill=tk.X, padx=5, pady=1)

            tk.Label(frame, text=symbol, bg='#34495e', fg='white',
                    font=('Arial', 10)).pack(side=tk.LEFT)
            tk.Label(frame, text=desc, bg='#34495e', fg='#bdc3c7',
                    font=('Arial', 9), anchor='w').pack(side=tk.LEFT, padx=(5, 0))

        # Parámetros
        params_frame = tk.LabelFrame(stats_frame, text="⚙️ Parámetros", bg='#34495e', fg='white',
                                    font=('Arial', 12, 'bold'))
        params_frame.pack(fill=tk.X, padx=10, pady=10)

        params_text = f"r={r}, d={d}, e={e}\nn={n}, u={u}"
        tk.Label(params_frame, text=params_text, bg='#34495e', fg='#bdc3c7',
                font=('Arial', 9), justify=tk.LEFT).pack(padx=5, pady=5)
    
    def run_batch_comparison(self, num_runs=10, ticks=500):
        results_auto = []
        results_static = []

        for sim_type in ["auto", "static"]:
            for _ in range(num_runs):
                if sim_type == "auto":
                    sim = Simulation()
                else:
                    sim = StaticSimulation(green_time=6, yellow_time=2, red_time=6)
                tick_count = 0
                while tick_count < ticks:
                    sim.step()
                    tick_count += 1
                # Calcular flujo promedio total
                total_A = sum(cA for (_, cA, cB) in sim.log)
                total_B = sum(cB for (_, cA, cB) in sim.log)
                avg_flow_total = (total_A + total_B) / ticks
                if sim_type == "auto":
                    results_auto.append(avg_flow_total)
                else:
                    results_static.append(avg_flow_total)

        avg_auto = sum(results_auto) / num_runs
        avg_static = sum(results_static) / num_runs

        messagebox.showinfo(
            "Comparación de Flujo Promedio",
            f"Simulaciones por tipo: {num_runs}\nTicks por simulación: {ticks}\n\n"
            f"Autoorganizada: {avg_auto:.2f} vehículos/tick\n"
            f"Estática: {avg_static:.2f} vehículos/tick"
        )

    def reset_simulation(self, static=False):
        self.running = False
        self.paused = False
        self.tick_count = 0

        # Elegir tipo de simulación según el radiobutton
        if self.sim_type.get() == "static":
            
            self.simulation = StaticSimulation(green_time=6, yellow_time=2, red_time=6)
        else:
            self.simulation = Simulation()

        # Actualizar estadísticas
        self.update_stats()
        # Dibujar estado inicial
        self.draw_simulation()

    def start_simulation(self):
        if not self.running:
            self.running = True
            self.paused = False
            # Ejecutar simulación en hilo separado
            thread = threading.Thread(target=self.run_simulation_thread)
            thread.daemon = True
            thread.start()

    def pause_simulation(self):
        self.paused = not self.paused
        if self.paused and self.simulation and self.tick_count > 0:
            # Calcular flujo promedio
            total_A = sum(cA for (_, cA, cB) in self.simulation.log)
            total_B = sum(cB for (_, cA, cB) in self.simulation.log)
            total_crossed = total_A + total_B
            avg_flow_A = total_A / self.tick_count
            avg_flow_B = total_B / self.tick_count
            avg_flow_total = total_crossed / self.tick_count
            sim_type_str = "Estática" if self.sim_type.get() == "static" else "Autoorganizada"
            messagebox.showinfo(
                "Promedio de Flujo",
                f"🚗 Flujo promedio actual ({sim_type_str}):\n"
                f"A = {avg_flow_A:.2f}  |  B = {avg_flow_B:.2f}  |  Total = {avg_flow_total:.2f} vehículos/tick"
            )

    def run_simulation_thread(self):
        while self.running and self.tick_count < MAX_TICKS:
            if not self.paused:
                # Avanzar un paso
                self.simulation.step()
                self.tick_count += 1

                # Actualizar interfaz en el hilo principal
                self.root.after(0, self.update_display)

            # Pausa basada en velocidad
            time.sleep(self.speed_var.get())

        self.running = False

    def update_display(self):
        self.draw_simulation()
        self.update_stats()

    def update_stats(self):
        if self.simulation:
            # Calcular estadísticas
            total_A = sum(cA for (_, cA, cB) in self.simulation.log)
            total_B = sum(cB for (_, cA, cB) in self.simulation.log)
            total_crossed = total_A + total_B
            efficiency = total_crossed / max(1, self.tick_count)

            # NUEVO: Flujo promedio por semáforo y total
            avg_flow_A = total_A / max(1, self.tick_count)
            avg_flow_B = total_B / max(1, self.tick_count)
            avg_flow_total = total_crossed / max(1, self.tick_count)

            # Actualizar labels
            self.stats_labels["tick"].config(text=str(self.tick_count))

            # NUEVO: Mostrar flujo promedio en la ventana
            if not hasattr(self, 'flow_label'):
                self.flow_label = tk.Label(self.root, text="", bg='#2c3e50', fg='#00ff99', font=('Arial', 12, 'bold'))
                self.flow_label.place(x=20, y=660)  # Ajusta la posición si lo deseas

            sim_type_str = "Estática" if self.sim_type.get() == "static" else "Autoorganizada"
            self.flow_label.config(
                text=f"🚗 Flujo promedio ({sim_type_str}):  A = {avg_flow_A:.2f}  |  B = {avg_flow_B:.2f}  |  Total = {avg_flow_total:.2f} vehículos/tick"
            )

            # Estados de semáforos con colores
            light_colors = {'RED': '🔴', 'YELLOW': '🟡', 'GREEN': '🟢'}
            stateA = light_colors.get(self.simulation.lightA.state, self.simulation.lightA.state)
            stateB = light_colors.get(self.simulation.lightB.state, self.simulation.lightB.state)

            self.stats_labels["lightA"].config(text=f"{stateA} ({self.simulation.lightA.time_in_state})")
            self.stats_labels["lightB"].config(text=f"{stateB} ({self.simulation.lightB.time_in_state})")

            self.stats_labels["carsA"].config(text=str(self.simulation.roadA.count_behind_red()))
            self.stats_labels["carsB"].config(text=str(self.simulation.roadB.count_behind_red()))
            self.stats_labels["crossedA"].config(text=str(total_A))
            self.stats_labels["crossedB"].config(text=str(total_B))
            self.stats_labels["totalCrossed"].config(text=str(total_crossed))
            self.stats_labels["efficiency"].config(text=f"{efficiency:.2f}/tick")

    def draw_simulation(self):
        self.canvas.delete("all")

        # Coordenadas centrales
        center_x = CANVAS_WIDTH // 2
        center_y = CANVAS_HEIGHT // 2

        # Dibujar intersección
        self.draw_intersection(center_x, center_y)

        # Dibujar carreteras y vehículos
        self.draw_road_horizontal(center_x, center_y, self.simulation.roadA, 'A')
        self.draw_road_vertical(center_x, center_y, self.simulation.roadB, 'B')

        # Dibujar semáforos
        self.draw_traffic_lights(center_x, center_y)

    def draw_intersection(self, center_x, center_y):
        # Intersección principal
        intersection_size = ROAD_WIDTH + 20
        self.canvas.create_rectangle(
            center_x - intersection_size//2, center_y - intersection_size//2,
            center_x + intersection_size//2, center_y + intersection_size//2,
            fill='#2c3e50', outline='#34495e', width=3
        )

        # Líneas de carretera horizontales
        self.canvas.create_rectangle(
            0, center_y - ROAD_WIDTH//2,
            CANVAS_WIDTH, center_y + ROAD_WIDTH//2,
            fill='#34495e', outline='#7f8c8d', width=2
        )

        # Líneas de carretera verticales
        self.canvas.create_rectangle(
            center_x - ROAD_WIDTH//2, 0,
            center_x + ROAD_WIDTH//2, CANVAS_HEIGHT,
            fill='#34495e', outline='#7f8c8d', width=2
        )

        # Líneas divisorias
        self.canvas.create_line(center_x, 0, center_x, center_y - intersection_size//2,
                               fill='yellow', width=2, dash=(5, 5))
        self.canvas.create_line(center_x, center_y + intersection_size//2, center_x, CANVAS_HEIGHT,
                               fill='yellow', width=2, dash=(5, 5))
        self.canvas.create_line(0, center_y, center_x - intersection_size//2, center_y,
                               fill='yellow', width=2, dash=(5, 5))
        self.canvas.create_line(center_x + intersection_size//2, center_y, CANVAS_WIDTH, center_y,
                               fill='yellow', width=2, dash=(5, 5))

    def draw_road_horizontal(self, center_x, center_y, road, name):
        # Calcular posiciones
        lane_y = center_y - ROAD_WIDTH//4 if name == 'A' else center_y + ROAD_WIDTH//4

        # Dibujar vehículos en approach (llegando desde la izquierda)
        for i, has_car in enumerate(road.approach):
            if has_car:
                x = 50 + i * 40  # Espaciado de vehículos

                # Color según zona
                if i >= IN_LENGTH - r:  # Zona crítica
                    color = '#e74c3c'  # Rojo
                elif i >= IN_LENGTH - d:  # Zona de detección
                    color = '#f39c12'  # Naranja
                else:
                    color = '#3498db'  # Azul

                self.draw_car(x, lane_y, color, '→')

        # Dibujar vehículos en exit_lane (saliendo hacia la derecha)
        for i, has_car in enumerate(road.exit_lane):
            if has_car:
                x = center_x + 50 + i * 40

                # Color según zona
                if i < e:  # Zona de salida
                    color = '#f1c40f'  # Amarillo
                else:
                    color = '#3498db'  # Azul

                self.draw_car(x, lane_y, color, '→')

    def draw_road_vertical(self, center_x, center_y, road, name):
        # Calcular posiciones
        lane_x = center_x - ROAD_WIDTH//4 if name == 'B' else center_x + ROAD_WIDTH//4

        # Dibujar vehículos en approach (llegando desde arriba)
        for i, has_car in enumerate(road.approach):
            if has_car:
                y = 50 + i * 40

                # Color según zona
                if i >= IN_LENGTH - r:  # Zona crítica
                    color = '#e74c3c'  # Rojo
                elif i >= IN_LENGTH - d:  # Zona de detección
                    color = '#f39c12'  # Naranja
                else:
                    color = '#3498db'  # Azul

                self.draw_car(lane_x, y, color, '↓')

        # Dibujar vehículos en exit_lane (saliendo hacia abajo)
        for i, has_car in enumerate(road.exit_lane):
            if has_car:
                y = center_y + 50 + i * 40

                # Color según zona
                if i < e:  # Zona de salida
                    color = '#f1c40f'  # Amarillo
                else:
                    color = '#3498db'  # Azul

                self.draw_car(lane_x, y, color, '↓')

    def draw_car(self, x, y, color, direction):
        # Dibujar rectángulo del carro
        self.canvas.create_rectangle(
            x - CAR_SIZE//2, y - CAR_SIZE//3,
            x + CAR_SIZE//2, y + CAR_SIZE//3,
            fill=color, outline='white', width=1
        )

        # Dibujar dirección
        self.canvas.create_text(x, y, text=direction, fill='white', font=('Arial', 8, 'bold'))


    def draw_traffic_lights(self, center_x, center_y):
        # Posiciones de los semáforos (A = izquierda, B = arriba)
        lights_pos = {
            'A': (center_x - 100, center_y - 40),  # Izquierda (más a la izquierda)
            'B': (center_x - 40, center_y - 120)   # Arriba (más arriba)
        }

        # Colores "apagados" (hex válidos) y colores cuando están activos
        off_colors = ['#4d0000', '#665500', '#003300']   # rojo apagado, amarillo apagado, verde apagado
        active_colors = {'RED': 'red', 'YELLOW': 'yellow', 'GREEN': 'green'}
        states = ['RED', 'YELLOW', 'GREEN']

        for light_name, (x, y) in lights_pos.items():
            light = getattr(self.simulation, f'light{light_name}')

            # Fondo del semáforo (caja)
            self.canvas.create_rectangle(
                x - 18, y - 28, x + 18, y + 28,
                fill='black', outline='gray', width=2
            )

            # Dibujar 3 leds (siempre dibujados; se selecciona color on/off)
            for i, state in enumerate(states):
                light_y = y - 14 + i * 18
                # color final: activo si coincide el estado, si no el color "apagado"
                final_color = active_colors[state] if light.state == state else off_colors[i]

                self.canvas.create_oval(
                    x - 10, light_y - 6, x + 10, light_y + 6,
                    fill=final_color, outline='white', width=1
                )

            # Etiqueta del semáforo
            self.canvas.create_text(x, y + 40, text=f'Semáforo {light_name}',
                                    fill='white', font=('Arial', 10, 'bold'))
