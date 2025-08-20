# cogs/ticket_system.py
# (O código das Views OpenTicketView e CloseTicketView continua o mesmo de antes)
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

class CloseTicketView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.danger, custom_id="fechar_ticket_button", emoji="🔒")
    async def fechar_ticket_callback(self, interaction: discord.Interaction, button: Button):
        # ... (código inalterado)
        membro_staff = interaction.user
        cargo_staff = discord.utils.get(interaction.guild.roles, name="Staff")
        if cargo_staff and cargo_staff in membro_staff.roles:
            await interaction.response.send_message(f"O ticket será fechado em 5 segundos por {membro_staff.mention}...", ephemeral=False)
            import asyncio
            await asyncio.sleep(5)
            await interaction.channel.delete(reason=f"Ticket fechado por {membro_staff.name}")
        else:
            await interaction.response.send_message("Apenas membros da equipe Staff podem fechar um ticket.", ephemeral=True)

    @discord.ui.button(label="Notificar Usuário", style=discord.ButtonStyle.secondary, custom_id="notificar_usuario_button", emoji="🔔")
    async def notificar_usuario_callback(self, interaction: discord.Interaction, button: Button):
        # ... (código inalterado)
        await interaction.response.defer(ephemeral=True, thinking=True)
        membro_staff = interaction.user
        cargo_staff = discord.utils.get(interaction.guild.roles, name="Staff")
        if not cargo_staff or cargo_staff not in membro_staff.roles:
            await interaction.followup.send("Apenas membros da equipe Staff podem usar este botão.", ephemeral=True)
            return
        ticket_owner = None
        for target in interaction.channel.overwrites:
            if isinstance(target, discord.Member) and target != self.bot.user:
                ticket_owner = target
                break
        if not ticket_owner:
            await interaction.followup.send("Não foi possível encontrar o dono deste ticket.", ephemeral=True)
            return
        try:
            dm_embed = discord.Embed(title="🔔 Notificação de Ticket", description=f"Olá! Um membro da equipe ({membro_staff.mention}) está aguardando sua resposta no seu ticket: {interaction.channel.mention}", color=discord.Color.yellow())
            await ticket_owner.send(embed=dm_embed)
            await interaction.followup.send(f"Notificação enviada com sucesso para {ticket_owner.mention}!", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("Não foi possível notificar o usuário. Ele pode ter desativado as mensagens privadas de membros do servidor.", ephemeral=True)

class OpenTicketView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.success, custom_id="abrir_ticket_button", emoji="🎟️")
    async def abrir_ticket_callback(self, interaction: discord.Interaction, button: Button):
        # ... (código inalterado)
        await interaction.response.defer(ephemeral=True, thinking=True)
        membro = interaction.user
        cargo_staff = discord.utils.get(interaction.guild.roles, name="Staff")
        categoria = discord.utils.get(interaction.guild.categories, name="TICKETS")
        if not categoria or not cargo_staff:
            await interaction.followup.send("ERRO DE CONFIGURAÇÃO: O cargo `Staff` ou a categoria `TICKETS` não foram encontrados.", ephemeral=True)
            return
        for channel in categoria.text_channels:
            if channel.name == f"ticket-{membro.name.lower()}":
                await interaction.followup.send(f"Você já tem um ticket aberto em {channel.mention}!", ephemeral=True)
                return
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            membro: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            cargo_staff: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        try:
            nome_canal = f"ticket-{membro.name.lower()}"
            canal_ticket = await interaction.guild.create_text_channel(name=nome_canal, category=categoria, overwrites=overwrites, reason=f"Ticket aberto por {membro.name}")
        except discord.Forbidden:
            await interaction.followup.send("ERRO: Não tenho permissão para criar canais.", ephemeral=True)
            return
        embed_boas_vindas = discord.Embed(title=f"Ticket de {membro.name}", description="Olá! Descreva seu problema ou dúvida em detalhes e aguarde a resposta de um membro da Staff. \n\nPara fechar este ticket, clique no botão abaixo.", color=discord.Color.green())
        await canal_ticket.send(content=f"{membro.mention}, seu ticket foi criado!", embed=embed_boas_vindas, view=CloseTicketView(self.bot))
        await interaction.followup.send(f"Seu ticket foi criado com sucesso em {canal_ticket.mention}!", ephemeral=True)

class TicketSystemCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(OpenTicketView(self.bot))
        self.bot.add_view(CloseTicketView(self.bot))
        print("Views do sistema de ticket registradas.")

    # --- CORREÇÃO DE ANONIMATO APLICADA AQUI ---
    @app_commands.command(name="painelticket", description="Envia o painel para abrir tickets no canal atual.")
    @app_commands.checks.has_permissions(administrator=True)
    async def painel_ticket(self, interaction: discord.Interaction):
        await interaction.response.send_message("Enviando o painel de tickets...", ephemeral=True)
        embed_painel = discord.Embed(
            title="🎟️ Suporte e Atendimento 🎟️",
            description="Precisa de ajuda ou tem alguma dúvida? Clique no botão abaixo para abrir um ticket privado com nossa equipe.",
            color=discord.Color.dark_blue()
        )
        view = OpenTicketView(self.bot)
        await interaction.channel.send(embed=embed_painel, view=view)
        await interaction.edit_original_response(content="Painel enviado com sucesso!")

async def setup(bot):
    await bot.add_cog(TicketSystemCog(bot))