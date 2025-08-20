# cogs/reaction_roles.py

import discord
from discord.ext import commands
from discord.ui import Button, View

# --- LÓGICA DOS BOTÕES ---

# Primeiro, definimos a nossa "View". Uma View é como um contêiner para componentes interativos como botões.
# O timeout=None faz com que os botões funcionem para sempre, mesmo que o bot reinicie.
class PainelCargos(View):
    def __init__(self):
        super().__init__(timeout=None)

    # Este é o nosso primeiro botão. O decorator define sua aparência e um ID único.
    @discord.ui.button(label="PC Gamer", style=discord.ButtonStyle.primary, custom_id="botao_cargo_pc")
    async def botao_cargo_pc_callback(self, interaction: discord.Interaction, button: Button):
        # 'interaction' contém todas as informações sobre quem clicou e onde.
        membro = interaction.user # O membro que clicou no botão.
        
        # Procuramos o cargo "PC Gamer" no servidor. O nome DEVE ser idêntico ao que você criou.
        cargo = discord.utils.get(membro.guild.roles, name="PC Gamer")

        # Verificamos se o cargo realmente existe para evitar erros.
        if cargo:
            # Se o membro já tiver o cargo, nós o removemos.
            if cargo in membro.roles:
                await membro.remove_roles(cargo)
                # 'ephemeral=True' faz a mensagem aparecer apenas para quem clicou.
                await interaction.response.send_message(f"Seu cargo '{cargo.name}' foi removido!", ephemeral=True)
            # Se ele não tiver o cargo, nós o adicionamos.
            else:
                await membro.add_roles(cargo)
                await interaction.response.send_message(f"Você recebeu o cargo '{cargo.name}'!", ephemeral=True)
        else:
            await interaction.response.send_message("ERRO: O cargo 'PC Gamer' não foi encontrado no servidor.", ephemeral=True)

    # Este é o segundo botão. A lógica é exatamente a mesma, só muda o nome do cargo.
    @discord.ui.button(label="Mobile Gamer", style=discord.ButtonStyle.green, custom_id="botao_cargo_mobile")
    async def botao_cargo_mobile_callback(self, interaction: discord.Interaction, button: Button):
        membro = interaction.user
        cargo = discord.utils.get(membro.guild.roles, name="Mobile Gamer")

        if cargo:
            if cargo in membro.roles:
                await membro.remove_roles(cargo)
                await interaction.response.send_message(f"Seu cargo '{cargo.name}' foi removido!", ephemeral=True)
            else:
                await membro.add_roles(cargo)
                await interaction.response.send_message(f"Você recebeu o cargo '{cargo.name}'!", ephemeral=True)
        else:
            await interaction.response.send_message("ERRO: O cargo 'Mobile Gamer' não foi encontrado no servidor.", ephemeral=True)

# --- LÓGICA DO COG ---

# Agora, criamos o Cog que vai conter o comando para enviar o painel.
class ReactionRolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Um listener especial que é acionado quando o Cog (e o bot) está pronto.
    @commands.Cog.listener()
    async def on_ready(self):
        # Isso registra nossa View com o bot, para que os botões continuem funcionando após uma reinicialização.
        self.bot.add_view(PainelCargos())

    # O comando que um admin vai usar para enviar o painel para um canal.
    @commands.command(name="painelcargos", help="Envia o painel de cargos por reação.")
    @commands.has_permissions(administrator=True) # Apenas administradores podem usar este comando.
    async def painel_cargos(self, ctx):
        embed_painel = discord.Embed(
            title="✨ Painel de Cargos ✨",
            description="Reaja com os botões abaixo para receber o cargo de sua plataforma preferida!",
            color=discord.Color.gold()
        )
        # Enviamos o embed e a nossa View com os botões.
        await ctx.send(embed=embed_painel, view=PainelCargos())

# A função setup que permite que o main.py carregue este Cog.
async def setup(bot):
    await bot.add_cog(ReactionRolesCog(bot))