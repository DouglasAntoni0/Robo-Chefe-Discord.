import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import asyncio
import datetime

# --- PERSONALIZE AQUI (DEIXE IGUAL À SUA FOTO) ---
TITULO_EMBED = "Suporte e atendimento" 
DESCRICAO_EMBED = "Precisa de ajuda, quer fazer um pedido ou tem alguma dúvida? Clique no botão abaixo para abrir um ticket privado com nossa equipe."
TEXTO_BOTAO_CRIAR = "Abrir Ticket" # O que vai estar escrito no botão verde
# --- CONFIGURAÇÕES TÉCNICAS ---
LOG_CHANNEL_NAME = "avaliações" # Nome exato do canal de logs

# --- 1. O FORMULÁRIO DE AVALIAÇÃO (MODAL) ---
class AvaliacaoModal(Modal, title="Avaliação de Atendimento"):
    nota = TextInput(label="Nota (1 a 5)", placeholder="Ex: 5", min_length=1, max_length=1)
    opiniao = TextInput(label="O que achou do atendimento?", style=discord.TextStyle.paragraph, placeholder="Digite sua opinião aqui...", required=True)
    sugestao = TextInput(label="Sugestões de melhoria (Opcional)", style=discord.TextStyle.paragraph, required=False)

    def __init__(self, bot, user, guild_name, original_message):
        super().__init__()
        self.bot = bot
        self.user = user
        self.guild_name = guild_name
        self.original_message = original_message # Guardamos a mensagem original para editar depois

    async def on_submit(self, interaction: discord.Interaction):
        # Agradece ao usuário
        await interaction.response.send_message("✅ **Obrigado!** Sua avaliação foi enviada com sucesso.", ephemeral=True)
        
        # --- AQUI ESTÁ A MÁGICA ---
        # Só agora, depois de enviar, a gente desativa o botão na DM do usuário
        try:
            view_desativada = BotaoAvaliar(self.bot, self.guild_name)
            for item in view_desativada.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = True
                    item.label = "Avaliação Enviada"
                    item.style = discord.ButtonStyle.grey
            await self.original_message.edit(view=view_desativada)
        except Exception as e:
            print(f"Erro ao desativar botão: {e}")

        # Envia para o canal de logs
        guild = interaction.client.get_guild(interaction.guild_id) if interaction.guild else None
        
        # Tenta achar o canal de logs em todos os servidores que o bot está
        log_channel = None
        for g in interaction.client.guilds:
            c = discord.utils.get(g.text_channels, name=LOG_CHANNEL_NAME)
            if c:
                log_channel = c
                break

        if log_channel:
            embed = discord.Embed(title="📊 Nova Avaliação Recebida", color=discord.Color.gold(), timestamp=datetime.datetime.now())
            embed.add_field(name="Cliente", value=f"{self.user.name} (ID: {self.user.id})", inline=False)
            embed.add_field(name="Nota", value=f"{self.nota.value}/5 ⭐", inline=True)
            embed.add_field(name="Opinião", value=self.opiniao.value, inline=False)
            if self.sugestao.value:
                embed.add_field(name="Sugestão", value=self.sugestao.value, inline=False)
            embed.set_footer(text=f"Enviado via Formulário")
            await log_channel.send(embed=embed)

# --- 2. BOTÃO QUE VAI PRO PRIVADO (PRA ABRIR O FORMULÁRIO) ---
class BotaoAvaliar(View):
    def __init__(self, bot, guild_name):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_name = guild_name

    @discord.ui.button(label="Responder Pesquisa de Satisfação", style=discord.ButtonStyle.blurple, emoji="📝")
    async def abrir_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Passamos a mensagem original (interaction.message) para o Modal
        await interaction.response.send_modal(AvaliacaoModal(self.bot, interaction.user, self.guild_name, interaction.message))
        # NÃO DESATIVAMOS O BOTÃO AQUI MAIS.
        # Ele só vai desativar lá no "on_submit" do Modal.

# --- 3. CONTROLES DENTRO DO TICKET (FECHAR E CHAMAR) ---
class TicketControls(View):
    def __init__(self):
        super().__init__(timeout=None)

    # Botão FECHAR TICKET (Com trava de ADMIN)
    @discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.red, custom_id="fechar_ticket_btn", emoji="🔒")
    async def fechar_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # VERIFICAÇÃO DE ADMIN (Se não for adm, não fecha)
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ **Apenas Administradores podem fechar o ticket!**", ephemeral=True)
            return

        await interaction.response.send_message("Fechando ticket e enviando formulário para o cliente...", ephemeral=True)
        
        channel = interaction.channel
        topic = channel.topic
        
        # Recupera o ID do usuário no tópico
        user_id = None
        if topic and "ID:" in topic:
            try:
                user_id = int(topic.split("ID: ")[1])
            except:
                pass

        await asyncio.sleep(2)
        await channel.delete()

        # Envia o botão de formulário no privado
        if user_id:
            user = interaction.guild.get_member(user_id)
            if user:
                try:
                    embed_dm = discord.Embed(title="Atendimento Encerrado", description=f"Olá! Seu ticket no servidor **{interaction.guild.name}** foi fechado.\nPor favor, dedique um segundo para nos avaliar clicando abaixo.", color=discord.Color.blue())
                    await user.send(embed=embed_dm, view=BotaoAvaliar(interaction.client, interaction.guild.name))
                except:
                    print(f"Não consegui enviar DM para {user.name}")

    # Botão CHAMAR USUÁRIO (Novo!)
    @discord.ui.button(label="Chamar Cliente", style=discord.ButtonStyle.secondary, custom_id="chamar_cliente_btn", emoji="🔔")
    async def chamar_cliente(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verifica se é adm
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Apenas Admins podem chamar o cliente.", ephemeral=True)
            return

        topic = interaction.channel.topic
        user_id = None
        if topic and "ID:" in topic:
            try:
                user_id = int(topic.split("ID: ")[1])
            except:
                pass
        
        if user_id:
            user = interaction.guild.get_member(user_id)
            if user:
                try:
                    # Manda mensagem no PV do cara
                    embed_aviso = discord.Embed(title="🔔 Atualização no seu Ticket", description=f"Olá! A equipe do **{interaction.guild.name}** respondeu seu ticket e está aguardando seu retorno.\n\nCorre lá no canal: {interaction.channel.mention}", color=discord.Color.orange())
                    await user.send(embed=embed_aviso)
                    await interaction.response.send_message(f"✅ Notificação enviada para o privado de {user.mention}!", ephemeral=True)
                except:
                    await interaction.response.send_message(f"❌ O cliente {user.mention} está com o privado bloqueado.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Cliente não está mais no servidor.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Erro: Não achei o ID do cliente no tópico do canal.", ephemeral=True)


# --- 4. O BOTÃO DE CRIAR TICKET (O PRIMEIRO DE TODOS) ---
class TicketLauncher(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label=TEXTO_BOTAO_CRIAR, style=discord.ButtonStyle.green, custom_id="criar_ticket_btn_v2", emoji="📩")
    async def criar_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        
        # Verifica se já tem ticket
        for channel in guild.text_channels:
            if channel.topic and f"ID: {interaction.user.id}" in channel.topic:
                await interaction.response.send_message("Ei, você já tem um ticket aberto!", ephemeral=True)
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        # Cria o canal
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            topic=f"Ticket de {interaction.user.name} | ID: {interaction.user.id}",
            overwrites=overwrites
        )

        await interaction.response.send_message(f"✅ Ticket criado: {channel.mention}", ephemeral=True)

        # Mensagem dentro do ticket novo
        embed = discord.Embed(title="Atendimento Iniciado", description="Olá! Descreva seu problema. A equipe administrativa logo irá atendê-lo.", color=discord.Color.green())
        
        # Aqui enviamos a view com os botões de Fechar e Chamar
        await channel.send(embed=embed, view=TicketControls())


# --- CLASSE PRINCIPAL DO SISTEMA ---
class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando para GERAR o painel (!setup_ticket)
    # Use este comando no canal onde você quer que a mensagem "igual da foto" apareça
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_ticket(self, ctx):
        await ctx.message.delete() # Apaga o comando que você digitou pra ficar limpo
        
        embed = discord.Embed(title=TITULO_EMBED, description=DESCRICAO_EMBED, color=discord.Color.dark_blue())
        # Se quiser colocar imagem, pode adicionar: embed.set_image(url="LINK_DA_IMAGEM")
        
        await ctx.send(embed=embed, view=TicketLauncher())

    @commands.Cog.listener()
    async def on_ready(self):
        print("--- Ticket System V3.1 (Formulário Inteligente) Carregado ---")
        self.bot.add_view(TicketLauncher())
        self.bot.add_view(TicketControls())

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
