# cogs/moderation_system.py

import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime

class ModerationSystemCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.warnings_file = "warnings.json"

    async def _load_warnings(self):
        if not os.path.exists(self.warnings_file):
            return {}
        with open(self.warnings_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    async def _save_warnings(self, warnings):
        with open(self.warnings_file, 'w', encoding='utf-8') as f:
            json.dump(warnings, f, indent=4)


    @app_commands.command(name="avisar", description="Aplica um aviso a um membro.")
    @app_commands.describe(membro="O membro que você quer avisar.", motivo="O motivo do aviso.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def avisar(self, interaction: discord.Interaction, membro: discord.Member, motivo: str):
        warnings = await self._load_warnings()
        timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

        novo_aviso = {
            "moderador_id": interaction.user.id,
            "moderador_nome": interaction.user.name,
            "motivo": motivo,
            "timestamp": timestamp
        }

        membro_id_str = str(membro.id)
        if membro_id_str not in warnings:
            warnings[membro_id_str] = []
        
        warnings[membro_id_str].append(novo_aviso)
        await self._save_warnings(warnings)

        embed_aviso = discord.Embed(
            title="✅ Aviso Aplicado",
            description=f"O membro {membro.mention} foi avisado.",
            color=discord.Color.red()
        )
        embed_aviso.add_field(name="Motivo", value=motivo, inline=False)
        embed_aviso.set_footer(text=f"Avisado por: {interaction.user.name}")

        await interaction.response.send_message(embed=embed_aviso)
        

    # --- NOSSO NOVO COMANDO ESTÁ AQUI ---
    
    @app_commands.command(name="avisos", description="Mostra o histórico de avisos de um membro.")
    @app_commands.describe(membro="O membro cujo histórico você quer ver.")
    async def avisos(self, interaction: discord.Interaction, membro: discord.Member):
        warnings = await self._load_warnings()
        membro_id_str = str(membro.id)

        # Verifica se o membro tem algum aviso registrado no arquivo
        if membro_id_str not in warnings or not warnings[membro_id_str]:
            embed_sem_avisos = discord.Embed(
                title=f"Histórico de Avisos de {membro.name}",
                description="Este membro tem um histórico limpo! Nenhum aviso encontrado.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed_sem_avisos)
            return # Encerra a função aqui

        # Se o membro tiver avisos, cria um Embed para listá-los
        embed_lista = discord.Embed(
            title=f"Histórico de Avisos de {membro.name}",
            color=discord.Color.orange()
        )
        embed_lista.set_thumbnail(url=membro.avatar.url if membro.avatar else None)

        # Faz um loop por cada aviso na lista do membro
        for i, aviso in enumerate(warnings[membro_id_str]):
            moderador = aviso.get('moderador_nome', 'Desconhecido')
            motivo = aviso.get('motivo', 'Nenhum motivo fornecido.')
            timestamp = aviso.get('timestamp', 'Data desconhecida')
            
            embed_lista.add_field(
                name=f"📝 Aviso #{i + 1} - Em {timestamp}",
                value=f"**Aplicado por:** {moderador}\n**Motivo:** {motivo}",
                inline=False
            )

        await interaction.response.send_message(embed=embed_lista)


async def setup(bot):
    await bot.add_cog(ModerationSystemCog(bot))