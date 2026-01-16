import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import asyncio
import datetime

# --- CONFIGURAÇÕES ---
SUPPORT_ROLE_ID = None 
LOG_CHANNEL_NAME = "logs-tickets" 

class TicketLauncher(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.green, custom_id="ticket_button_persistente", emoji="📩")
    async def ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        for channel in guild.text_channels:
            if channel.topic and f"ID: {interaction.user.id}" in channel.topic:
                await interaction.response.send_message("Ei, você já tem um ticket aberto! Termine o anterior primeiro.", ephemeral=True)
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        if SUPPORT_ROLE_ID:
            role = guild.get_role(SUPPORT_ROLE_ID)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            topic=f"Ticket de {interaction.user.name} | ID: {interaction.user.id}",
            overwrites=overwrites
        )

        await interaction.response.send_message(f"✅ Ticket criado com sucesso em {channel.mention}!", ephemeral=True)
        embed = discord.Embed(title="Atendimento Iniciado", description="Descreva seu problema. Um administrador logo irá atendê-lo.", color=discord.Color.blue())
        await channel.send(embed=embed, view=CloseButton())

class CloseButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fechar Ticket e Avaliar", style=discord.ButtonStyle.red, custom_id="close_ticket_btn_persistente", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Fechando ticket e iniciando pesquisa...", ephemeral=True)
        channel = interaction.channel
        topic = channel.topic
        user_id = None
        if topic and "ID:" in topic:
            try:
                user_id = int(topic.split("ID: ")[1])
            except:
                pass
        await asyncio.sleep(3)
        await channel.delete()
        if user_id:
            user = interaction.guild.get_member(user_id)
            if user:
                await self.start_survey(user, interaction.guild)

    async def start_survey(self, user, guild):
        def check(m):
            return m.author == user and isinstance(m.channel, discord.DMChannel)
        try:
            await user.send(f"Olá, {user.name}! 👋 Seu ticket no servidor **{guild.name}** foi encerrado.\n\nPara nos ajudar, responda rapidinho:\n\n1️⃣ **De 1 a 5, que nota você dá para o nosso atendimento?**")
            msg_nota = await user.client.wait_for('message', check=check, timeout=120)
            nota = msg_nota.content
            await user.send("📝 **O que você achou do atendimento?**")
            msg_opiniao = await user.client.wait_for('message', check=check, timeout=180)
            opiniao = msg_opiniao.content
            await user.send("💡 **O que podemos fazer para melhorar?**")
            msg_melhoria = await user.client.wait_for('message', check=check, timeout=180)
            melhoria = msg_melhoria.content
            await user.send("✅ **Muito obrigado!**")
            
            if LOG_CHANNEL_NAME:
                log_channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
                if log_channel:
                    embed_log = discord.Embed(title="📊 Avaliação de Atendimento", color=discord.Color.gold(), timestamp=datetime.datetime.now())
                    embed_log.add_field(name="Usuário", value=f"{user.name} (ID: {user.id})", inline=False)
                    embed_log.add_field(name="Nota", value=f"{nota}/5 ⭐", inline=True)
                    embed_log.add_field(name="Opinião", value=opiniao, inline=False)
                    embed_log.add_field(name="Sugestão", value=melhoria, inline=False)
                    await log_channel.send(embed=embed_log)
        except Exception as e:
            print(f"Erro na pesquisa: {e}")

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- COMANDO DE BARRA (/painelticket) ---
    @app_commands.command(name="painelticket", description="Cria o painel de tickets neste canal")
    @app_commands.checks.has_permissions(administrator=True)
    async def painelticket(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Central de Ajuda", description="Clique no botão abaixo para falar com a equipe.", color=discord.Color.brand_green())
        await interaction.response.send_message("Painel enviado!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=TicketLauncher())

    # Tirei o comando Sync daqui porque ele já existe no seu bot!

    @commands.Cog.listener()
    async def on_ready(self):
        print("--- Ticket System: Carregado ---")
        self.bot.add_view(TicketLauncher())
        self.bot.add_view(CloseButton())

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
