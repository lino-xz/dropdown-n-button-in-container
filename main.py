import sys
from datetime import datetime, timedelta, timezone
import discord
from discord import ui
from discord.ext import commands

TOKEN = "YOUR_BOT_TOKEN"
PREFIX = "$"

intents = discord.Intents.all()
VN_TZ = timezone(timedelta(hours=7))


def build_container(username: str, selected: str = "home") -> tuple[ui.Container, ui.Select]:
    timestamp = datetime.now(VN_TZ).strftime("%d/%m/%Y %H:%M")
    container = ui.Container()

    # Home page
    if selected == "home":
        container.add_item(ui.TextDisplay("## Components V2 Test"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay("-# Looking good"))
        container.add_item(ui.Separator())

        container.add_item(ui.TextDisplay("### Vanish Club"))
        container.add_item(ui.TextDisplay(
            "- **1:** Ktn\n"
            "- **2:** Lino\n"
            "- **3:** Pepsi"
        ))
        container.add_item(ui.Separator())

        container.add_item(ui.TextDisplay("### Commands"))
        container.add_item(ui.TextDisplay(
            "- `$help` - Show Components V2 example\n"
            "- `$demo` - Show Components V2 example\n"
            "- `$preview` - Show Components V2 example"
        ))

    # Bot information
    elif selected == "info":
        container.add_item(ui.TextDisplay("## Bot Information"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(
            "This bot is built using **discord.py** with Components V2!"
        ))

    # Ping test
    elif selected == "ping":
        container.add_item(ui.TextDisplay("## Ping Command"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(
            "Pong. Everything is running smoothly!"
        ))

    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(
        f"-# Requested by {username} • {timestamp}"
    ))
    container.add_item(ui.Separator())

    # Dropdown menu
    dropdown = ui.Select(
        placeholder="Choose an option...",
        options=[
            discord.SelectOption(label="Home Page", value="home", emoji="🏠", default=selected == "home"),
            discord.SelectOption(label="Bot Info", value="info", emoji="ℹ️", default=selected == "info"),
            discord.SelectOption(label="Ping Test", value="ping", emoji="🏓", default=selected == "ping"),
        ],
    )

    container.add_item(ui.ActionRow(dropdown))

    # Link buttons
    container.add_item(ui.ActionRow(
        ui.Button(label="Server", style=discord.ButtonStyle.link, url="https://discord.gg/your-invite"),
        ui.Button(label="YouTube", style=discord.ButtonStyle.link, url="https://youtube.com/@your-channel"),
    ))

    return container, dropdown


class SimpleLayoutView(ui.LayoutView):
    def __init__(self, author_id: int, username: str):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.username = username
        self.render("home")

    def render(self, selected: str):
        self.clear_items()

        container, dropdown = build_container(self.username, selected)
        dropdown.callback = self.on_select
        self.add_item(container)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ You cannot use this menu!",
                ephemeral=True
            )
            return False
        return True

    async def on_select(self, interaction: discord.Interaction):
        selected = interaction.data["values"][0]
        self.render(selected)
        await interaction.response.edit_message(view=self)


class CoreBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print("=" * 50)
        print(f"[+] Logged in as {self.user} | ID: {self.user.id}")
        print("=" * 50)


bot = CoreBot()


# Prefix command
@bot.command(name="help", aliases=["demo", "preview"])
async def help_command(ctx: commands.Context):
    view = SimpleLayoutView(ctx.author.id, ctx.author.name)
    await ctx.send(view=view)


# Slash command
@bot.tree.command(name="help", description="Show all available commands")
async def help_command_slash(interaction: discord.Interaction):
    view = SimpleLayoutView(interaction.user.id, interaction.user.name)
    await interaction.response.send_message(view=view, ephemeral=True)


if __name__ == "__main__":
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN":
        print("[!] Bot token is not configured!")
        sys.exit(1)

    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("[!] Invalid bot token!")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[!] Bot stopped!")
        