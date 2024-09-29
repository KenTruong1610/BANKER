import tkinter as tk
from tkinter import messagebox

# Hàm tính toán ma trận need từ max và allocation
def calculate_need(max_matrix, allocation_matrix):
    return [[max_matrix[i][j] - allocation_matrix[i][j] for j in range(len(max_matrix[0]))] for i in range(len(max_matrix))]

# Hàm kiểm tra nếu một yêu cầu có thể được chấp nhận
def check_request(available, need, request, process):
    for j in range(len(available)):
        if request[j] > need[process][j] or request[j] > available[j]:
            return False
    return True

# Hàm cấp phát tài nguyên sau khi yêu cầu được chấp nhận
def allocate_resources(available, allocation, need, request, process):
    for j in range(len(available)):
        available[j] -= request[j]
        allocation[process][j] += request[j]
        need[process][j] -= request[j]

# Hàm kiểm tra xem một tiến trình có thể thực hiện được không
def check_process(available, need, process):
    for j in range(len(available)):
        if need[process][j] > available[j]:
            return False
    return True

# Hàm cập nhật tài nguyên sẵn có
def update_available(available, allocation, process):
    for j in range(len(available)):
        available[j] += allocation[process][j]

# Hàm tìm chuỗi an toàn và cập nhật "Work" matrix
def find_sequence(available, need, allocation):
    n = len(need)
    sequence = []
    finished = [False] * n
    count = 0

    work_matrix = [available.copy()]  # Ma trận Work bắt đầu từ available
    
    work = available.copy()  # Biến Work để theo dõi tài nguyên khả dụng
    
    while count < n:
        found = False
        for i in range(n):
            if not finished[i] and all(need[i][j] <= work[j] for j in range(len(work))):
                # Cập nhật chuỗi an toàn
                sequence.append(f'P{i}')
                finished[i] = True
                count += 1
                
                # Cập nhật Work
                work = [work[j] + allocation[i][j] for j in range(len(work))]
                work_matrix.append(work.copy())  # Lưu lại trạng thái Work sau khi cấp phát
                
                found = True
                break

        if not found:
            return None, None  # Không tìm được chuỗi an toàn

    return sequence, work_matrix

# Hàm xử lý yêu cầu từ tiến trình được chọn
def handle_request():
    try:
        process = selected_process.get()  # Lấy tiến trình từ menu chọn
        request = list(map(int, request_entry.get().split()))

        if len(request) != len(available):
            messagebox.showerror("Error", "Yêu cầu phải có số lượng tài nguyên bằng số tài nguyên hiện tại.")
            return

        # Kiểm tra yêu cầu có hợp lệ
        if check_request(available.copy(), need_matrix, request, process):
            allocate_resources(available, allocation_matrix, need_matrix, request, process)
            result_text.set(f"Request từ P{process} đã được chấp nhận.\nTài nguyên mới: {' '.join(map(str, available))}")
        else:
            messagebox.showerror("Error", f"Request từ P{process} không thể thực hiện.")

        # Tính toán lại chuỗi an toàn và Work matrix
        sequence, work_matrix = find_sequence(available.copy(), need_matrix, allocation_matrix)

        if sequence:
            display_work_matrix(work_matrix, len(work_matrix), len(available))
            result_text.set(result_text.get() + f"\nChuỗi an toàn: " + " -> ".join(sequence))
        else:
            messagebox.showerror("Error", "Hệ thống không ở trạng thái an toàn!")

    except ValueError:
        messagebox.showerror("Invalid Input", "Hãy nhập yêu cầu hợp lệ.")

# Hàm để cập nhật giao diện dựa trên số tiến trình và số tài nguyên
def update_inputs():
    try:
        n_processes = int(n_proc_entry.get())
        n_resources = int(n_res_entry.get())

        # Xóa các mục nhập cũ
        for widget in frame_inputs.winfo_children():
            widget.destroy()

        global max_entries, allocation_entries, need_labels, need_matrix, allocation_matrix, process_menu
        max_entries = []
        allocation_entries = []
        need_labels = []
        allocation_matrix = []
        need_matrix = []

        # Cập nhật menu chọn tiến trình
        selected_process.set(0)
        process_menu['menu'].delete(0, 'end')
        for i in range(n_processes):
            process_menu['menu'].add_command(label=f'P{i}', command=tk._setit(selected_process, i))

        for i in range(n_processes):
            # Nhãn và ô nhập cho ma trận Max
            tk.Label(frame_inputs, text=f"P{i} Max (R1 R2 ...):").grid(row=i, column=0, padx=10, pady=5)
            max_entry = tk.Entry(frame_inputs)
            max_entry.grid(row=i, column=1, padx=10, pady=5)
            max_entries.append(max_entry)

            # Nhãn và ô nhập cho ma trận Allocation
            tk.Label(frame_inputs, text=f"P{i} Allocation (R1 R2 ...):").grid(row=i, column=2, padx=10, pady=5)
            allocation_entry = tk.Entry(frame_inputs)
            allocation_entry.grid(row=i, column=3, padx=10, pady=5)
            allocation_entries.append(allocation_entry)

            # Nhãn hiển thị ma trận Need
            need_label = tk.Label(frame_inputs, text="Need: ")
            need_label.grid(row=i, column=4, padx=10, pady=5)
            need_labels.append(need_label)

    except ValueError:
        messagebox.showerror("Invalid Input", "Vui lòng nhập số hợp lệ cho tiến trình và tài nguyên.")

# Hàm để tính toán và hiển thị ma trận Need, chuỗi an toàn và Work matrix
def calculate_sequence():
    try:
        n_processes = int(n_proc_entry.get())
        n_resources = int(n_res_entry.get())

        # Lấy tài nguyên sẵn có
        global available, allocation_matrix, need_matrix
        available = list(map(int, available_entry.get().split()))

        max_matrix = []
        allocation_matrix = []

        for i in range(n_processes):
            max_matrix.append(list(map(int, max_entries[i].get().split())))
            allocation_matrix.append(list(map(int, allocation_entries[i].get().split())))

        # Tính toán ma trận Need
        need_matrix = calculate_need(max_matrix, allocation_matrix)

        # Hiển thị ma trận Need
        for i in range(n_processes):
            need_labels[i].config(text=f"Need: {' '.join(map(str, need_matrix[i]))}")

        # Tìm chuỗi an toàn và ma trận Work
        sequence, work_matrix = find_sequence(available.copy(), need_matrix, allocation_matrix)

        if sequence:
            result_text.set("Chuỗi an toàn: " + " -> ".join(sequence))
            # Hiển thị ma trận Work
            display_work_matrix(work_matrix, n_processes, n_resources)
        else:
            messagebox.showerror("Error", "Hệ thống không ở trạng thái an toàn!")
    except ValueError:
        messagebox.showerror("Invalid Input", "Hãy nhập giá trị hợp lệ cho tài nguyên và tiến trình.")

# Hàm hiển thị ma trận Work
def display_work_matrix(work_matrix, n_processes, n_resources):
    # Xóa nội dung cũ trong ô Work
    for widget in frame_work.winfo_children():
        widget.destroy()

    # Thêm nhãn tiêu đề
    tk.Label(frame_work, text="Work", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=n_resources, padx=10, pady=5)
    
    # Thêm tiêu đề cột (R1, R2, R3, ...)
    for j in range(n_resources):
        tk.Label(frame_work, text=f"R{j+1}", font=("Arial", 10)).grid(row=1, column=j, padx=10, pady=5)
    
    # Thêm ma trận Work
    for i in range(len(work_matrix)):
        for j in range(n_resources):
            tk.Label(frame_work, text=f"{work_matrix[i][j]}", bg="white", width=5, height=2, borderwidth=1, relief="solid").grid(row=i+2, column=j, padx=5, pady=5)

# Thiết kế giao diện
root = tk.Tk()
root.title("Banker's Algorithm - 31231022130")

# Nhãn và ô nhập số tiến trình
tk.Label(root, text="Số tiến trình:").grid(row=0, column=0, padx=10, pady=5)
n_proc_entry = tk.Entry(root)
n_proc_entry.grid(row=0, column=1, padx=10, pady=5)

# Nhãn và ô nhập số tài nguyên
tk.Label(root, text="Số tài nguyên:").grid(row=1, column=0, padx=10, pady=5)
n_res_entry = tk.Entry(root)
n_res_entry.grid(row=1, column=1, padx=10, pady=5)

# Nút cập nhật giao diện đầu vào
tk.Button(root, text="Cập nhật", command=update_inputs).grid(row=1, column=2, padx=10, pady=5)

# Khung cho các ô nhập Max, Allocation và Need
frame_inputs = tk.Frame(root)
frame_inputs.grid(row=7, column=0, columnspan=3, padx=10, pady=5)

# Khung cho Work matrix
frame_work = tk.Frame(root)
frame_work.grid(row=8, column=0, columnspan=3, padx=10, pady=5)

# Nhãn và ô nhập tài nguyên sẵn có
tk.Label(root, text="Available (R1 R2 ...):").grid(row=3, column=0, padx=10, pady=5)
available_entry = tk.Entry(root)
available_entry.grid(row=3, column=1, padx=10, pady=5)

# Nút tính toán chuỗi an toàn
tk.Button(root, text="Tính toán chuỗi an toàn", command=calculate_sequence).grid(row=10, column=2, padx=10, pady=5)

# Chọn tiến trình để thực hiện yêu cầu
tk.Label(root, text="Chọn tiến trình:").grid(row=6, column=0, padx=10, pady=5)
selected_process = tk.IntVar()
process_menu = tk.OptionMenu(root, selected_process, [])
process_menu.grid(row=6, column=1, padx=10, pady=5)

# Nhập yêu cầu tài nguyên từ tiến trình
tk.Label(root, text="Yêu cầu tài nguyên (R1 R2 ...):").grid(row=5, column=0, padx=10, pady=5)
request_entry = tk.Entry(root)
request_entry.grid(row=5, column=1, padx=10, pady=5)

# Nút thực hiện yêu cầu
tk.Button(root, text="Thực hiện yêu cầu", command=handle_request).grid(row=6, column=2, padx=10, pady=5)

# Hiển thị kết quả
result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, font=("Arial", 12)).grid(row=9, column=0, columnspan=3, padx=10, pady=10)

# Khởi động ứng dụng
root.mainloop()
