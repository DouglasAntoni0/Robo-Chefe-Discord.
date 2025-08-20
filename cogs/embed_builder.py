# cogs/embed_builder.py

import discord
from discord import app_commands
from discord.ext import commands

# --- O FORMULÁRIO (MODAL) ---
class EmbedBuilderModal(discord.ui.Modal, title="Criador de Anúncios (Embed)"):
    
    titulo = discord.ui.TextInput(
        label="Título do Embed",
        placeholder="Ex: Atualização do Servidor - 19.08",
        style=discord.TextStyle.short,
        required=True
    )

    descricao = discord.ui.TextInput(
        label="Descrição / Conteúdo Principal",
        placeholder="Use **texto** para negrito. Para emojis, use o formato <:nome:id>.",
        style=discord.TextStyle.paragraph,
        required=True
    )

    cor = discord.ui.TextInput(
        label="Cor da Barra Lateral (Código Hex)",
        placeholder="Ex: #3498db (Azul). Deixe em branco para a cor padrão.",
        style=discord.TextStyle.short,
        required=False
    )
    
    mencao = discord.ui.TextInput(
        label="Menção (Opcional)",
        placeholder="Ex: @everyone ou o nome de um cargo.",
        style=discord.TextStyle.short,
        required=False
    )
    
    url_imagem_rodape = discord.ui.TextInput(
        label="URL da Imagem do Rodapé (Opcional)",
        placeholder="https://imgur.com/link_da_imagem.png",
        style=discord.TextStyle.short,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # --- TÉCNICA DE ANONIMATO CORRIGIDA ---
            # 1. Responde imediatamente à interação de forma invisível.
            await interaction.response.send_message("Criando seu embed...", ephemeral=True)

            # 2. Agora, faz todo o trabalho de construir o embed.
            hex_color = self.cor.value.replace("#", "")
            final_color = discord.Color.blue()
            if hex_color:
                final_color = discord.Color(int(hex_color, 16))

            embed = discord.Embed(
                title=self.titulo.value,
                description=self.descricao.value,
                color=final_color,
                timestamp=discord.utils.utcnow()
            )

            if self.url_imagem_rodape.value:
                embed.set_footer(icon_url=self.url_imagem_rodape.value)

            mensagem_a_enviar = self.mencao.value if self.mencao.value else None

            # 3. Envia o embed como uma mensagem nova, completamente separada.
            await interaction.channel.send(content=mensagem_a_enviar, embed=embed)

            # 4. (Opcional) Edita a mensagem invisível para confirmar que deu tudo certo.
            await interaction.edit_original_response(content="Embed enviado com sucesso!")

        except Exception as e:
            print(f"Erro ao processar o modal de embed: {e}")
            await interaction.followup.send("Ocorreu um erro inesperado ao tentar enviar o embed.", ephemeral=True)


# --- O COG ---
class EmbedBuilderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="criar-embed", description="Abre um formulário para criar um anúncio anônimo (Embed).")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def criar_embed(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EmbedBuilderModal())

# Função setup para carregar o Cog
async def setup(bot):
    await bot.add_cog(EmbedBuilderCog(bot))