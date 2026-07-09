import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_diagram():
    # Set size and DPI for high quality
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    
    # Hide axis lines and ticks
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")
    
    # Font properties
    font_title = {"fontsize": 12, "fontweight": "bold", "color": "#1E293B", "family": "sans-serif"}
    font_subtitle = {"fontsize": 10, "fontweight": "bold", "color": "#0F172A", "family": "sans-serif"}
    font_body = {"fontsize": 9, "color": "#334155", "family": "sans-serif"}
    font_header = {"fontsize": 16, "fontweight": "bold", "color": "#1E3A8A", "family": "sans-serif"}
    
    # Draw overall title in Vietnamese
    ax.text(6.5, 7.5, "KIẾN TRÚC ĐÁNH GIÁ HỆ THỐNG LANCERAI", ha="center", va="center", **font_header)
    
    # ─── BOX 1: INPUT DATASETS (Left Column) ───
    # X: 0.5 -> 3.7 (width 3.2), Y: 1.5 -> 6.5 (height 5.0)
    box_input = patches.FancyBboxPatch((0.5, 1.5), 3.2, 5.0, boxstyle="round,pad=0.1", 
                                       facecolor="#F1F5F9", edgecolor="#CBD5E1", linewidth=1.5)
    ax.add_patch(box_input)
    ax.text(2.1, 6.3, "1. Tập Dữ Liệu Kiểm Thử\n(Golden Datasets)", ha="center", va="center", **font_title)
    
    # Sub-items in datasets
    items_datasets = [
        ("Hồ sơ ứng viên (CV)", "50 CV IT thực tế\n(Đã ẩn danh thông tin)"),
        ("Mô tả công việc (JD)", "50 JD tuyển dụng IT\n(Cào thực tế từ TopCV)"),
        ("Lượt thoại ghi âm (Audio)", "50 File ghi âm giọng nói\n(Định dạng PCM 16kHz)")
    ]
    for idx, (title, desc) in enumerate(items_datasets):
        y_pos = 5.0 - idx * 1.5
        # Draw small item card
        card = patches.FancyBboxPatch((0.7, y_pos - 0.5), 2.8, 0.9, boxstyle="round,pad=0.05",
                                      facecolor="#FFFFFF", edgecolor="#E2E8F0", linewidth=1)
        ax.add_patch(card)
        ax.text(2.1, y_pos + 0.1, title, ha="center", va="center", **font_subtitle)
        ax.text(2.1, y_pos - 0.2, desc, ha="center", va="center", **font_body)

    # ─── BOX 2: SYSTEM CORE (Center Block) ───
    box_core = patches.FancyBboxPatch((4.5, 3.2), 4.0, 1.8, boxstyle="round,pad=0.1",
                                      facecolor="#EEF2F6", edgecolor="#3B82F6", linewidth=2)
    ax.add_patch(box_core)
    ax.text(6.5, 4.5, "Lõi Hệ Thống LancerAI", ha="center", va="center", **font_title)
    ax.text(6.5, 3.8, "Bộ Điều Phối Đa Tác Tử\n(FastAPI & Celery Pipeline)", ha="center", va="center", **font_subtitle)

    # ─── BOX 3: OFFLINE EVALUATION (Top Right) ───
    # X: 9.3 -> 12.8 (width 3.5), Y: 4.2 -> 6.5 (height 2.3)
    box_offline = patches.FancyBboxPatch((9.3, 4.2), 3.4, 2.3, boxstyle="round,pad=0.1",
                                         facecolor="#F0FDFA", edgecolor="#0D9488", linewidth=1.5)
    ax.add_patch(box_offline)
    ax.text(11.0, 6.2, "2A. Đánh Giá Ngoại Tuyến\n(Offline Evaluation)", ha="center", va="center", **font_title)
    
    offline_items = [
        "• Khung đánh giá RAGAS\n  (Độ trung thực & Độ liên quan)",
        "• Tỷ lệ lỗi từ (WER)\n  (Độ chính xác nhận diện STT)",
        "• Đo lường hiệu năng (Latency)\n  (Thời gian TTFT & E2E)"
    ]
    # Shifted Y coordinates up (from 5.2 to 5.5, step 0.5) to keep text within the box boundaries
    for idx, item in enumerate(offline_items):
        ax.text(9.5, 5.5 - idx * 0.5, item, ha="left", va="center", **font_body)

    # ─── BOX 4: ONLINE EVALUATION (Bottom Right) ───
    # X: 9.3 -> 12.8 (width 3.5), Y: 1.2 -> 3.5 (height 2.3)
    box_online = patches.FancyBboxPatch((9.3, 1.2), 3.4, 2.3, boxstyle="round,pad=0.1",
                                        facecolor="#FFFBEB", edgecolor="#D97706", linewidth=1.5)
    ax.add_patch(box_online)
    ax.text(11.0, 3.2, "2B. Đánh Giá Trực Tuyến\n(Online Evaluation)", ha="center", va="center", **font_title)
    
    online_items = [
        "• Phản hồi từ người dùng\n  (Khảo sát Google Form CSAT)",
        "• Nhật ký hành vi (Telemetry)\n  (Tỷ lệ hoàn thành buổi phỏng vấn)",
        "• Khôi phục kết nối mạng\n  (Tự kết nối lại WebSocket)"
    ]
    # Shifted Y coordinates up (from 2.2 to 2.5, step 0.5) to keep text within the box boundaries
    for idx, item in enumerate(online_items):
        ax.text(9.5, 2.5 - idx * 0.5, item, ha="left", va="center", **font_body)

    # ─── DRAW ARROWS (Flows) ───
    # From Datasets to Core
    ax.annotate("", xy=(4.4, 4.0), xytext=(3.8, 4.0),
                arrowprops=dict(facecolor='#334155', edgecolor='#334155', shrink=0.05, width=1.5, headwidth=6))
    
    # From Core to Offline
    ax.annotate("", xy=(9.2, 5.3), xytext=(8.4, 4.5),
                arrowprops=dict(facecolor='#0D9488', edgecolor='#0D9488', shrink=0.05, width=1.5, headwidth=6))

    # From Core to Online
    ax.annotate("", xy=(9.2, 2.3), xytext=(8.4, 3.5),
                arrowprops=dict(facecolor='#D97706', edgecolor='#D97706', shrink=0.05, width=1.5, headwidth=6))

    # Save image to absolute path
    output_path = r"C:\Users\DUY\LancerAI\scratch\evaluation_architecture.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"Diagram successfully generated at: {output_path}")

if __name__ == "__main__":
    draw_diagram()
