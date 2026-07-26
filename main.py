import os
import sys
from datetime import datetime, timezone, timedelta
import discord
from discord.ext import commands
from discord.ui import (
    LayoutView,
    Container,
    TextDisplay,
    Separator,
    ActionRow,
    Button,
    Select,
)

BOT_TOKEN: str = "YOUR_BOT_TOKEN"
COMMAND_PREFIX: str = "."
gateway_intents = discord.Intents.all()

# Định nghĩa múi giờ Việt Nam (UTC+7)
VN_TZ = timezone(timedelta(hours=7))


def build_simple_container(user_name: str, selected_option: str = "home") -> tuple[Container, Select]:
    # Lấy thời gian hiện tại theo múi giờ Việt Nam
    formatted_time = datetime.now(VN_TZ).strftime("%d/%m/%Y %H:%M")

    # Tạo Container + xoá viền dọc
    container = Container(accent_color=None)

    # 1. Tạo nội dung hiển thị (TextDisplay)
    if selected_option == "home":
        container.add_item(TextDisplay("## Components V2 Test"))
        container.add_item(TextDisplay("-# Đẹp trai vl"))
        container.add_item(Separator())
        main_content = (
            "### Vanish Club\n"
            "- **1:** Ktn\n"
            "- **2:** Lino\n"
            "- **3:** Pepsi\n\n"
            "### Commands\n"
            "- `.help` - Show simple components V2 example\n"
            "- `.demo` - Show simple components V2 example\n"
            "- `.preview` - Show simple components V2 example"
        )
        container.add_item(TextDisplay(main_content))
    elif selected_option == "info":
        container.add_item(TextDisplay("## Bot Information"))
        container.add_item(TextDisplay("This bot is built using **discord.py** with Components V2!"))
    elif selected_option == "ping":
        container.add_item(TextDisplay("## Ping Command"))
        container.add_item(TextDisplay("Pong! Everything is running smoothly"))

    # Thêm đường kẻ và footer
    container.add_item(Separator())
    container.add_item(TextDisplay(f"-# Requested by {user_name} • {formatted_time}"))
    container.add_item(Separator())

    # 2. Tạo menu kéo (DropdownSelect)
    dropdown = Select(
        placeholder="Choose an option...",
        options=[
            discord.SelectOption(label="Home Page", value="home", emoji="🏠", default=(selected_option == "home")),
            discord.SelectOption(label="Bot Info", value="info", emoji="ℹ️", default=(selected_option == "info")),
            discord.SelectOption(label="Ping Test", value="ping", emoji="🏓", default=(selected_option == "ping")),
        ]
    )

    # Bắt buộc đặt Dropdown vào trong ActionRow trước khi thêm vào Container
    container.add_item(ActionRow(dropdown))

    # 3. Tạo khay chứa button (Button)
    action_row_buttons = ActionRow(
        Button(label="Server", style=discord.ButtonStyle.link, url="https://discord.gg/your-invite"),
        Button(label="YouTube", style=discord.ButtonStyle.link, url="https://youtube.com/@your-channel")
    )
    container.add_item(action_row_buttons)

    return container, dropdown


class SimpleLayoutView(LayoutView):
    def __init__(self, author_id: int, user_name: str):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.user_name = user_name
        
        # Mặc định render trang "home" khi khởi tạo
        self.render("home")

    def render(self, option: str):
        """Hàm cập nhật/vẽ lại giao diện dựa theo tab được chọn"""
        self.clear_items()  # Dọn dẹp toàn bộ thành phần cũ trên View
        
        # Gọi hàm tạo Container mới
        container, dropdown = build_simple_container(self.user_name, option)
        
        # Gán callback xử lý sự kiện khi người dùng chọn Dropdown
        dropdown.callback = self.on_select
        
        # Thêm Container đã cấu hình vào LayoutView
        self.add_item(container)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ You cannot use this menu!", ephemeral=True)
            return False
        return True

    async def on_select(self, interaction: discord.Interaction):
        """Lắng nghe và xử lý sự kiện khi chọn 1 item trong Dropdown"""
        # Lấy giá trị 'value' của tùy chọn vừa bấm
        selected = interaction.data["values"][0]
        
        # Cập nhật lại giao diện tương ứng
        self.render(selected)
        
        # Sửa tin nhắn ban đầu để cập nhật giao diện mới
        await interaction.response.edit_message(view=self)


class CoreBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=COMMAND_PREFIX, 
            intents=gateway_intents, 
            help_command=None 
        )

    async def setup_hook(self) -> None:
        """Đồng bộ Slash Commands nếu cần sử dụng"""
        await self.tree.sync()

    async def on_ready(self) -> None:
        print(f"==================================================")
        print(f"[✓] Bot logged in as: {self.user} | ID: {self.user.id}")
        print(f"==================================================")

bot = CoreBot()

# 1. Prefix Commands
@bot.command(name="help", aliases=["demo", "preview"])
async def help_command(ctx: commands.Context) -> None:
    view = SimpleLayoutView(author_id=ctx.author.id, user_name=ctx.author.name)
    await ctx.send(view=view)


# 2. Slash Commands
@bot.tree.command(name="help", description="Show simple components V2 example")
async def help(interaction: discord.Interaction):
    view = SimpleLayoutView(author_id=interaction.user.id, user_name=interaction.user.name)
    await interaction.response.send_message(view=view, ephemeral=True)


if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_BOT_TOKEN" or not BOT_TOKEN:
        print("[!] ERROR: Token trống hoặc chưa cấu hình!")
        sys.exit(1)
        
    try:
        bot.run(BOT_TOKEN)
    except discord.errors.LoginFailure:
        print("[!] ERROR: Token không hợp lệ!")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[!] Bot đã dừng!")
        