# cogs/general_commands.py
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime


class GeneralCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sobre",
                          description="Mostra informações sobre o bot.")
    async def sobre_slash(self, interaction: discord.Interaction):
        embed_sobre = discord.Embed(
            title="Painel de Ajuda do CHEFE",
            description="Estes são os comandos que eu conheço até agora!",
            color=discord.Color.blue())
        embed_sobre.set_author(name=self.bot.user.name,
                               icon_url=self.bot.user.avatar.url
                               if self.bot.user.avatar else None)
        embed_sobre.add_field(name="`/sobre`",
                              value="Mostra este painel de ajuda.",
                              inline=False)
        embed_sobre.add_field(name="`/hora`",
                              value="Mostra a data e hora atuais.",
                              inline=False)
        embed_sobre.add_field(name="`/falar`",
                              value="Faz o bot enviar uma mensagem anônima.",
                              inline=False)
        embed_sobre.set_footer(
            text=f"Comando solicitado por: {interaction.user.name}")

        await interaction.response.send_message(embed=embed_sobre)

    @app_commands.command(name="hora",
                          description="Mostra a data e hora atuais.")
    async def hora_slash(self, interaction: discord.Interaction):
        agora = datetime.now()
        hora_formatada = agora.strftime('%H:%M:%S')
        data_formatada = agora.strftime('%d/%m/%Y')
        # --- LINHA CORRIGIDA ABAIXO ---
        await interaction.response.send_message(
            f'Agora são {hora_formatada} do dia {data_formatada}.')

    @app_commands.command(
        name="falar",
        description="Faz o bot enviar uma mensagem anônima no canal.")
    @app_commands.describe(mensagem="O texto que o bot deve falar.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def falar_slash(self, interaction: discord.Interaction,
                          mensagem: str):
        await interaction.response.send_message(
            "Mensagem enviada com sucesso!", ephemeral=True)
        await interaction.channel.send(mensagem)

    async def cog_app_command_error(self, interaction: discord.Interaction,
                                    error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "Você não tem permissão para usar este comando!",
                ephemeral=True)
        else:
            print(
                f"Ocorreu um erro não tratado no Cog 'GeneralCommands': {error}"
            )
            await interaction.response.send_message(
                "Ocorreu um erro ao tentar executar este comando.",
                ephemeral=True)


async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))
