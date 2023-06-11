from nextcord import Embed, Colour, ButtonStyle
from nextcord.ext import commands
from nextcord.ui import button, View
from nextcord.ext.commands import Bot, Context

class TestView(View):
    def __init__(self):
        super().__init__(timeout=None) # timeout of the view must be set to None

    @button(label="Kill me please", custom_id="button-1", style=ButtonStyle.primary, emoji="💀")
    async def button_callback(self, button, interaction):
        await interaction.response.send_message("Button was pressed", ephemeral=True)

class ButtonTest(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(description="Test buttons")
    async def buttontest(self, ctx: Context):
        view = TestView()
        await ctx.send("Press the button", view=view)
